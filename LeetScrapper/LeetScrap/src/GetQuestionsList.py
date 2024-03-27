import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error
from bs4 import BeautifulSoup
import time
import datetime
import socket
import os
from tqdm import tqdm
import json
from _constants import CATEGORIES, TOPIC_TAGS
from helper import camel_case


class GetQuestionsList:
    """A class to scrape the list of questions, their topic tags, and company tags.

    Args:
        limit (int, optional): The maximum number of questions to query for from Leetcode's graphql API. Defaults to 10,000.
    """

    # Specify the path to the JSON file which contains the database credentials
    json_path = "_db_config.json"

    # Read the database credentials from the JSON file
    with open(json_path, "r") as file:
        content = file.read()

    # Parse the database credentials
    db_config = json.loads(content)

    # Get the current system's name
    system_name = socket.gethostname()

    # Get the current system's IP address
    ip_address = socket.gethostbyname(system_name)

    # using getlogin() returning username
    host_name = os.getlogin()

    def __init__(self, limit: int = 10000):
        self.limit = limit
        self.description = pd.DataFrame()
        self.questions = pd.DataFrame()
        self.questionLink = pd.DataFrame()

    def scrape(self):
        """Scrapes LeetCode data including company tags, questions, question topics,
        and categories.
        """

        self._scrape_questions_list()
        self._get_categories_and_topicTags_lists()
        self._scrape_question_category()
        self._scrape_question_link()
        self._add_category_to_questions_list()

    def _get_categories_and_topicTags_lists(self):
        """Get the categories and topic tags of LeetCode problems and store them in the
        'categories' and 'topicTags' attribute respectively."""
        print("Getting Categories ... ", end="")
        # List of problem categories
        self.categories = pd.DataFrame.from_records(CATEGORIES)
        print("Done")
        # List of problem topic tags
        print("Scraping Topic Tags ... ", end="")
        self.topicTags = pd.DataFrame.from_records(TOPIC_TAGS)
        print("Done")

    def _scrape_question_category(self):
        """Scrape the category of each question and store it in the 'questionCategory' dataframe."""
        print("Extracting question category ... ", end="")
        categories_data = []
        for category in self.categories["slug"].values:
            data = {
                "query": """query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
                        problemsetQuestionList: questionList(
                            categorySlug: $categorySlug
                            limit: $limit
                            skip: $skip
                            filters: $filters
                        ) {
                            questions: data {
                                QID: questionFrontendId
                            }
                        }
                    }
                """,
                "variables": {
                    "categorySlug": category,
                    "skip": 0,
                    "limit": self.limit,
                    "filters": {},
                },
            }

            r = requests.post("https://leetcode.com/graphql", json=data).json()
            categories = pd.json_normalize(
                r["data"]["problemsetQuestionList"]["questions"]
            )
            categories["categorySlug"] = category
            categories_data.append(categories)
        self.questionCategory = pd.concat(
            categories_data, axis=0, ignore_index=True)
        print("Done")

    def _scrape_question_link(self):
        """Scrape the orignal links of each question and store it in the 'OrignalLinks' dataframe."""
        print("Scraping question links ... ", end="")
        original_links = []
        for title_slug in self.questions["titleSlug"].values:
            link = "https://leetcode.com/problems/" + title_slug + "/"
            original_links.append({"titleSlug": title_slug, "link": link})
        self.questionLink = pd.DataFrame(original_links)

        # Merge questions_df with questionLink DataFrame based on 'titleSlug'
        merged_df = pd.merge(
            self.questions, self.questionLink, on="titleSlug", how="left")
        self.questions = merged_df

        print("Done")

    def _scrape_questions_list(self):
        """
        Scrapes the list of questions from leetcode.com and store them in the 'questions'
        dataframe. The columns include the question QID, acceptance rate, difficulty,
        title, titleSlug, and topic tags. It also has a column indicating
        whether the question is available only to Leetcode's paying customers.
        """
        print("Scraping questions list ... ", end="")
        data = {
            "query": """query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
                problemsetQuestionList: questionList(
                    categorySlug: $categorySlug
                    limit: $limit
                    skip: $skip
                    filters: $filters
                ) {
                    total: totalNum
                    questions: data {
                        acceptanceRate: acRate
                        difficulty
                        QID: questionFrontendId
                        paidOnly: isPaidOnly
                        title
                        titleSlug
                        topicTags {
                            slug
                        }
                    }
                }
            }""",
            "variables": {
                "categorySlug": "",
                "skip": 0,
                "limit": self.limit,
                "filters": {},
            },
        }

        r = requests.post("https://leetcode.com/graphql", json=data).json()

        # Check if the response structure is as expected
        if 'data' in r and 'problemsetQuestionList' in r['data']:
            self.questions = pd.json_normalize(
                r["data"]["problemsetQuestionList"]["questions"]
            )[
                [
                    "QID",
                    "title",
                    "titleSlug",
                    "difficulty",
                    "acceptanceRate",
                    "paidOnly",
                    "topicTags",
                ]
            ]
            self.questions["topicTags"] = self.questions["topicTags"].apply(
                lambda w: [tag["slug"] for tag in w]
            )

            # Convert the acceptance rate to an integer
            self.questions["acceptanceRate"] = self.questions["acceptanceRate"].apply(
                lambda w: int(w) if w is not None else None
            )

            self.questions = self.questions.drop(
                self.questions[self.questions["paidOnly"] == True].index)

            print("Done")
        else:
            print("Unexpected response structure:", r)

    def _add_category_to_questions_list(self):
        """Adds the `topicTags` column containing the comma-separated string of
        the list of topic tags relevant to the given questions and the `category`
        column that includes the category relevant to the given question"""
        self.questions["topicTags"] = self.questions["topicTags"].apply(
            lambda w: ", ".join(w)
        )
        self.questions = self.questions.join(
            self.questionCategory.set_index("QID"), on="QID"
        )

    def to_csv(self, directory_path: str) -> None:
        """A method to export the scraped data into csv files in preparation for
        injection into a database.

        Args:
            directory_path (str): The directory path to export the scraped data into.
        """

        self.questions.to_csv(directory_path + "questions.csv", index=False)

    def db_to_data(self, url, db_config):
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        try:
            if connection.is_connected():
                cursor = connection.cursor()

                sql = "SELECT OriginalLink FROM question_master_coding WHERE OriginalLink = %s"
                cursor.execute(sql, (url,))
                val = cursor.fetchall()
                connection.commit()

                if (len(val) == 0):
                    return True

                return False

        except Error as e:
            print("Error while connecting to MySQL", e)
            print(url)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                # print("MySQL connection is closed")

    def to_sql(self, db_config) -> None:
        """A method to export the scraped data into a MySQL database.

        Args:
            db_config (dict): A dictionary containing the MySQL database connection details.
                             It should include the following keys: "host", "user", "password", "database".
        """
        print("Exporting data to Navicat database ... ", end="")

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert data into the table
        insert_query = """
            INSERT INTO question_master_coding(Session, Topic, Title, QuestionLevel, OriginalLink, Uploaded_By, Uploaded_On, Uploaded_From, QuestionMark, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        for _, row in self.questions.iterrows():
            if (self.db_to_data(row['link'], db_config)):
                data = ('2023-2024', row['topicTags'], row['title'], row['difficulty'], row['link'], 'Arunodaya.Singh_cs21 | ' +
                        GetQuestionsList.host_name, datetime.datetime.now().isoformat(' ', 'seconds'), GetQuestionsList.ip_address, 1, 'PENDING')
                cursor.execute(insert_query, data)

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        print("Done")

    def to_json(self, directory_path: str) -> None:
        """A method to export the scraped data into json files in preparation for
        injection into a database.

        Args:
            directory_path (str): The directory path to export the scraped data into.
        """
        self.questions.to_json(
            directory_path + "questions.json", orient="records")

        # Specify the file path to the JSON file
        json_file_path = directory_path
        if (json_file_path[-1] != "/"):
            json_file_path += "/questions.json"
        else:
            json_file_path += "questions.json"

        # Open and read the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        # print(data[7])
