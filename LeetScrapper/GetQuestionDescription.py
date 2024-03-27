from bs4 import BeautifulSoup
import requests
import time
import json
import mysql.connector
from mysql.connector import Error
from tqdm import tqdm


class GetQuestionDescription:
    """A class to scrape the description of all questions.

    Args:
        limit (int, optional): The maximum number of questions to query for from Leetcode's graphql API. Defaults to 10,000.
    """

    # Specify the path to the JSON file
    json_path = "_db_config.json"

    # Read the JSON file
    with open(json_path, "r") as file:
        content = file.read()

    # Parse the JSON content
    db_config = json.loads(content)

    def __init__(self, limit: int = 10000):
        self.limit = limit
        self.questions = None

    def scrape(self):
        """Scrapes LeetCode data of questions examples.
        """

        self._get_question()

    def _get_question(self):

        print("Scraping question description...", end="")
        # getting the url list from the database
        url_list = GetQuestionDescription.db_to_data(
            GetQuestionDescription.db_config)
        for url in enumerate(tqdm(url_list)):
            questions_list = []     # list to store the questions description
            links = url[1][0]       # getting the url from the list
            r = requests.get(links)  # sending request to the url
            html_text = r.text  # getting the html text
            # parsing the html text using lxml parser
            soup = BeautifulSoup(html_text, 'lxml')
            # finding the div tag with class flex h-full w-full flex-1 flex-col
            question = soup.find(
                'div', class_='flex h-full w-full flex-1 flex-col')     # finding the div tag which is containg main material of the Question
            if question is None:        # if the question is not found because of the high traffic or loading issue
                continue
            else:
                # description of the question
                description_beautify = question.find('div', class_='_1l1MA')

                # Remove all <img> tags
                for img in description_beautify.find_all('img'):
                    img.decompose()

                # Remove all 'href' attributes
                for a in description_beautify.find_all('a'):
                    del a['href']

                # Convert the html content in description to a string
                description = str(description_beautify)
                # Count the total number of <pre> tags
                total_pre = description.count("<pre>")
                temp_pre_ends = 0   # Variable to store the temporary end index of the <pre> tag

                time.sleep(1)
                for i in range(total_pre):
                    # Find the start index of the <pre> tag
                    pre_index_starts = description.find("<pre>", temp_pre_ends)
                    pre_index_ends = description.find(
                        "</pre>", pre_index_starts)     # Find the end index of the <pre> tag
                    description = description[:pre_index_starts] + \
                        "<div style='background-color:#000a2050; padding: 2px 0px 2px 20px'>" + \
                        description[pre_index_starts:pre_index_ends] + \
                        "</div>" + \
                        description[pre_index_ends:]     # Add a <div> tag around each <pre> tag
                    temp_pre_ends = description.find(
                        "</pre>", pre_index_starts)     # Update the end index for next interation

                # Add the styling to the <code> tag
                description = description.replace(
                    "<code>", "<code style='background-color:#000a2050; max-width:fit-content; padding: 3px 5px 3px 5px'>")

                # Add the orignal styling to the <li> tag
                description = description.replace(
                    "<li>", "<li style='margin-bottom:5px'>")

                # Add a line break before each <strong> tag
                description = description.replace("\n<strong>", "<br><strong>")

                # Add the original styling of the <strong> tag
                description = description.replace(
                    "<strong>", "<strong style='margin=10 0 10 0'>")
                # Remove all unnecessary line breaks
                description = description.replace("\n", "")

                # Update the extracted style attribute to get question in its original format
                description = description.replace(
                    'style="width:253px;height:253px"', 'style="width:253px;height:253px; margin: 0 0 15px 0"')

                # Create a BeautifulSoup object
                soup = BeautifulSoup(description, "html.parser")

                # Find and remove the specific code blocks
                code_blocks = soup.find_all(
                    "div", style="background-color:#000a2050; padding: 2px 0px 2px 20px")
                for code_block in code_blocks:
                    if code_block is not None:
                        code_block.extract()

                # Remove the example sections
                examples = soup.find_all("strong", class_="example")
                for example in examples:

                    if example.parent is not None:
                        example.parent.extract()  # Remove the parent element containing the example

                    if example.parent.next_sibling:
                        example.parent.next_sibling.extract()  # Remove the associated <div> element

                # Print the modified HTML
                description = str(soup.prettify())

                # Add a line break before each <strong> tag
                description = description.replace("\n<strong>", "<br><strong>")
                # Remove all unnecessary line breaks
                description = description.replace("\n", "")
                description = description.replace(
                    "</code>", "</code>&nbsp;")  # Add a non-breaking space after each </code> tag

                questions_list.append({"Link": links, "Question": description})

                GetQuestionDescription.data_to_db(
                    self, questions_list, GetQuestionDescription.db_config)

        print("Done")

    def db_to_data(db_config: dict) -> list:
        # connecting to the database using the connect() method
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()    # creating a cursor object using the cursor() method
        try:
            if connection.is_connected():       # Checking if the connection is established
                # Executing SQL Queries using the execute() method
                cursor = connection.cursor()

                # Executing SQL Queries using the execute() method
                sql = "SELECT OriginalLink FROM question_master_coding WHERE Question IS NULL"
                # Fetch all the rows using the fetchall() method
                cursor.execute(sql)
                val = cursor.fetchall()     # Printing the result one by one
                connection.commit()     # Commiting the changes
                return val
        except Error as e:
            # Handling the connection error
            print("Error while connecting to MySQL\n\n", e)
        finally:
            if connection.is_connected():
                cursor.close()      # Closing the cursor object
                connection.close()      # Closing the connection
                print("MySQL connection is closed\n\n")

    def data_to_db(self, question, db_config: dict):
        # connecting to the database using the connect() method
        connection = mysql.connector.connect(**db_config)
        # creating a cursor object using the cursor() method
        cursor = connection.cursor()
        try:
            if connection.is_connected():
                # creating a cursor object using the cursor() method
                cursor = connection.cursor()

                if question not in [None, []]:
                    # Preparing SQL query to INSERT a record into the database.
                    question_sql = "UPDATE question_master_coding SET Question = %s WHERE OriginalLink = %s"

                    values = [question[0]["Question"], question[0]
                              ["Link"]]     # Preparing a list of values to be inserted into the database.
                    # Executing the SQL command
                    cursor.execute(question_sql, values)

                    # commiting the connection then closing it.
                    connection.commit()
                    # sleep for 2 seconds once the data is inserted so that the database is not overloaded with multiple requests
                    time.sleep(2)
                else:
                    # calling the get_question() function
                    question = GetQuestionDescription.get_question()

        except Error as e:
            # Printing the link of the question where the error occured
            print(question[0]["Link"])
            # Handling the connection error
            print("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()      # Closing the cursor object
                connection.close()      # Closing the connection
