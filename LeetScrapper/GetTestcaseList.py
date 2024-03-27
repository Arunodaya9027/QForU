import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import json


class GetTestcaseList:
    """A class to scrape the list of test cases from each question.

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
        """Scrapes LeetCode questions sample test cases.
        """

        self._get_testcase()

    def _get_testcase(self):
        """Scrape the sample test cases of each question and store it in the 'testcase' json object."""

        print("Scraping questions testcase ... ", end="")
        # Create an instance of the class
        questions_detailed = GetTestcaseList.db_to_data(
            self, GetTestcaseList.db_config)
        flag = 0
        for l, url in enumerate(tqdm(questions_detailed)):
            if GetTestcaseList.duplicacy_data(self, GetTestcaseList.db_config, l+1):
                QID = l + 1
                links = questions_detailed[l][0]
                r = requests.get(links)  # sending request to the url

                time.sleep(1)  # pausing the execution for 1 sec

                html_text = r.text  # getting the html text
                # parsing the html text using lxml parser
                soup = BeautifulSoup(html_text, 'lxml')
                # finding the div tag with class flex h-full w-full flex-1 flex-col
                question = soup.find(
                    'div', class_='flex h-full w-full flex-1 flex-col')
                if question is None:
                    print("Error: ", links)

                else:
                    # description of the question
                    description_beautify = question.find(
                        'div', class_='_1l1MA')
                    description = str(description_beautify)
                    total_pre = description.count(
                        '<p><strong class="example">Example')
                    temp_pre_start = description.find(
                        '<strong class="example">Example')

                    description = description.replace("<strong>Input</strong>", "<strong>Input:</strong>").replace("<strong>Input: </strong>", "<strong>Input:</strong>").replace("<strong>Output</strong>", "<strong>Output:</strong>").replace("<strong>Output: </strong>", "<strong>Output:</strong>").replace("<strong>Explanation</strong>", "<strong>Explanation:</strong>").replace("<strong>Explanation: </strong>", "<strong>Explanation:</strong>").replace(
                        "<strong>Explanation : </strong>", "<strong>Explanation:</strong>").replace("<strong>Explanation :</strong>", "<strong>Explanation:</strong>").replace("<b>Input:</b>", "<strong>Input:</strong>").replace("<b>Output:</b>", "<strong>Output:</strong>").replace("<b>Explanation:</b>", "<strong>Explanation:</strong>").replace("<b>Explanation  :</b>", "<strong>Explanation:</strong>").replace("<b>Explanation  : </b>", "<strong>Explanation:</strong>")

                    time.sleep(2)  # pausing the execution for 2 sec
                    if (description.count('<strong>Input:</strong>') == 0):
                        continue
                    else:
                        for i in range(total_pre):
                            pre_index_starts = description.find(
                                "<strong>Input:</strong>", temp_pre_start)
                            pre_index_ends = description.find(
                                "<strong>Output:</strong>", pre_index_starts)
                            input = description[pre_index_starts +
                                                len("<strong>Input:</strong>"):pre_index_ends]
                            temp_pre_start = pre_index_starts + 1

                            pre_index_starts = description.find(
                                "<strong>Output:</strong>", temp_pre_start)
                            pre_index_ends = description.find(
                                "<strong>Explanation:</strong>", pre_index_starts)
                            temp_pre_ends = description.find(
                                '<strong class="example">Example', temp_pre_start)

                            if (temp_pre_ends < pre_index_ends and temp_pre_ends != -1) or pre_index_ends == -1:
                                pre_index_ends = description.find(
                                    "</pre>", pre_index_starts)
                                if ("Explanation:" in description[pre_index_starts+len("<strong>Output:</strong>"):pre_index_ends]):
                                    temp_end = description.find(
                                        "Explanation:", pre_index_starts)
                                    output = description[pre_index_starts +
                                                         len("<strong>Output:</strong>"):temp_end]
                                    explanation = description[temp_end +
                                                              len("Explanation:"):pre_index_ends]
                                else:
                                    output = description[pre_index_starts+len(
                                        "<strong>Output:</strong>"):pre_index_ends]
                                    temp_pre_start = pre_index_starts + 1
                                    explanation = ""

                            else:
                                output = description[pre_index_starts +
                                                     len("<strong>Output:</strong>"):pre_index_ends]
                                temp_pre_start = pre_index_starts + 1

                                pre_index_starts = description.find(
                                    "<strong>Explanation:</strong>", temp_pre_start)
                                pre_index_ends = description.find(
                                    "</pre>", pre_index_starts)
                                explanation = description[pre_index_starts+len(
                                    "<strong>Explanation:</strong>"):pre_index_ends]
                                temp_pre_start = pre_index_starts + 1

                            time.sleep(1)  # pausing the execution for 1 sec

                            testcase = {"QuestionID": QID, "TCNo": i+1, "Input": input.strip().strip("\n").strip("\t").strip("\r"),
                                        "Output": output.strip().strip("\n").strip("\t").strip("\r"), "Explanation": explanation.strip().strip("\n").strip("\t").strip("\r")}
                            # questions_detailed.append(testcase)
                            GetTestcaseList.to_sql(
                                self, GetTestcaseList.db_config, testcase)

        print("Done")

    def db_to_data(self, db_config):
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        try:
            if connection.is_connected():
                cursor = connection.cursor()
                sql = "SELECT OriginalLink FROM question_master_coding"
                cursor.execute(sql)
                val = cursor.fetchall()
                connection.commit()
                return val

        except Error as e:
            print("Error while connecting to MySQL", e)
            print()
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def duplicacy_data(self, db_config, QID):
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        try:
            if connection.is_connected():
                cursor = connection.cursor()
                sql = "SELECT Question_Id FROM question_master_testcase_coding WHERE Question_Id = %s"
                cursor.execute(sql, [QID])
                val = cursor.fetchall()
                connection.commit()
                if (len(val) == 0):
                    return True
                return False

        except Error as e:
            print("Error while connecting to MySQL", e)
            print()
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def to_sql(self, db_config, testcase):
        """A method to export the scraped data of test cases into a MySQL database.

        Args:
            db_config (dict): A dictionary containing the MySQL database connection details.
                             It should include the following keys: "host", "user", "password", "database".
        """

        connection = mysql.connector.connect(**db_config)

        try:
            if connection.is_connected():
                cursor = connection.cursor()
                # Insert data into the table
                insert_query = "INSERT INTO question_master_testcase_coding (Question_Id, TestCaseNo, Custom_Input, Custom_Output, Explanation) VALUES(%s, %s, %s, %s, %s);"
                values = [testcase["QuestionID"], testcase["TCNo"],
                          testcase["Input"], testcase["Output"], testcase["Explanation"]]

                cursor.execute(insert_query, values)
                connection.commit()

        except Error as e:
            print("Error while connecting to MySQL", e)
            print()
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
