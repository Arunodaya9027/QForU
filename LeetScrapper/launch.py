from GetQuestionsList import GetQuestionsList
from GetTestcaseList import GetTestcaseList
from GetExampleList import GetExampleList
from GetQuestionDescription import GetQuestionDescription
import mysql.connector
from mysql.connector import Error
import json


class launch_scraper:
    # Specify the path to the JSON file
    json_path = "_db_config.json"

    # Read the JSON file
    with open(json_path, "r") as file:
        content = file.read()

    # Parse the JSON content
    db_config = json.loads(content)

    def __init__(self):
        print("Launching scraper...")
        self._get_db(launch_scraper.db_config)

    def _get_db(self, db_config):
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("You're connected to database: ", record)

                tables_all = "SHOW TABLES;"
                flag_master_table, flag_testcase_table, flag_example_table = False, False, False
                cursor.execute(tables_all)
                tables = cursor.fetchall()
                for table in tables:
                    if table[0] == "question_master_coding":
                        flag_master_table = True
                    elif table[0] == "question_master_testcase_coding":
                        flag_testcase_table = True
                    elif table[0] == "question_master_detail_coding":
                        flag_example_table = True

                if flag_master_table == False and flag_testcase_table == False and flag_example_table == False:
                    self._create_table(db_config)
                    print("Tables created successfully")

                elif flag_master_table == True and flag_testcase_table == True and flag_example_table == True:
                    print("Connecting Tables from Database to Scraper ...")

                elif flag_master_table == True or flag_testcase_table == True or flag_example_table == True:
                    print("Mismatching of Tables Found")
                    print("Some tables exist, some don't. Please check the database")

        except Error as e:
            print("Error while connecting to MySQL", e)
            print()

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                # print("MySQL connection is closed")

    def _create_table(self, db_config):
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        try:
            if connection.is_connected():
                cursor = connection.cursor()
                key = "SET FOREIGN_KEY_CHECKS=0;"

                # Table structure for `question_master_testcase_coding`
                sql = """CREATE TABLE `question_master_testcase_coding` (
                    `id` bigint NOT NULL AUTO_INCREMENT,
                    `Question_Id` bigint DEFAULT NULL,
                    `TestCaseNo` int DEFAULT NULL,
                    `Custom_Input` longtext,
                    `Custom_Output` longtext,
                    `Explanation` longtext CHARACTER SET latin1 COLLATE latin1_swedish_ci,
                    PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB AUTO_INCREMENT=5138 DEFAULT CHARSET=latin1;"""
                cursor.execute(key)
                cursor.execute(sql)
                connection.commit()

                key = "SET FOREIGN_KEY_CHECKS=0;"

                # Table structure for `question_master_coding_temp`
                sql = """CREATE TABLE `question_master_coding` (
                    `Question_ID` bigint NOT NULL AUTO_INCREMENT,
                    `Session` varchar(255) DEFAULT NULL,
                    `Subject_Code` varchar(255) DEFAULT NULL,
                    `Topic` longtext CHARACTER SET latin1 COLLATE latin1_swedish_ci,
                    `TopicID` bigint DEFAULT NULL,
                    `Title` longtext CHARACTER SET latin1 COLLATE latin1_swedish_ci,
                    `Question` longtext CHARACTER SET latin1 COLLATE latin1_swedish_ci,
                    `QuestionLevel` varchar(255) DEFAULT NULL,
                    `OriginalLink` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
                    `Status` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT '' COMMENT 'ACTIVE',
                    `Uploaded_By` varchar(255) DEFAULT NULL,
                    `Uploaded_On` datetime DEFAULT NULL,
                    `Uploaded_From` varchar(255) DEFAULT NULL,
                    `DeletedBy` varchar(255) DEFAULT NULL,
                    `DeletedOn` datetime DEFAULT NULL,
                    `DeletedFrom` varchar(255) DEFAULT NULL,
                    `DeletedRemark` varchar(255) DEFAULT NULL,
                    `QuestionMark` int DEFAULT '1',
                    `QuestionMode` varchar(255) DEFAULT 'Coding Problem',
                    `QuestionType` varchar(255) DEFAULT 'Academic',
                    `QuestionFor` varchar(255) DEFAULT 'Main',
                    `ExpectedAnswer` longtext,
                    `VerifyBy` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
                    `VerifyOn` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
                    `VerifyFrom` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
                    PRIMARY KEY (`Question_ID`),
                    KEY `a` (`Subject_Code`) USING BTREE,
                    KEY `b` (`Session`) USING BTREE,
                    KEY `c` (`Question_ID`) USING BTREE,
                    KEY `d` (`Status`) USING BTREE,
                    KEY `e` (`TopicID`) USING BTREE,
                    KEY `f` (`QuestionLevel`) USING BTREE,
                    KEY `g` (`Status`) USING BTREE,
                    KEY `i` (`QuestionMark`) USING BTREE,
                    KEY `j` (`QuestionMode`) USING BTREE,
                    KEY `k` (`QuestionType`) USING BTREE
                    ) ENGINE=InnoDB AUTO_INCREMENT=2254 DEFAULT CHARSET=latin1;

                    """
                cursor.execute(key)
                cursor.execute(sql)
                connection.commit()

                key = "SET FOREIGN_KEY_CHECKS=0;"

                # Table structure for `question_master_detail_coding_temp`
                sql = """CREATE TABLE `question_master_detail_coding` (
                    `id` bigint NOT NULL AUTO_INCREMENT,
                    `Question_Id` bigint DEFAULT NULL,
                    `ExampleNo` int DEFAULT NULL,
                    `Input` longtext,
                    `ExpectedOutput` longtext,
                    `Explanation` longtext,
                    PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB AUTO_INCREMENT=8373 DEFAULT CHARSET=latin1;"""
                cursor.execute(key)
                cursor.execute(sql)
                connection.commit()

        except Error as e:
            print("Error while connecting to MySQL", e)
            print()

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def question_list_scrape(self):
        ls = GetQuestionsList()
        ls.scrape()  # Scrape the list of questions
        ls.to_sql(ls.db_config)  # Save the list of questions to a SQL database

    def get_description(self):
        gd = GetQuestionDescription()
        gd.scrape()  # Scrape the description of all questions

    def test_scrape(self):
        ts = GetTestcaseList()
        ts.scrape()  # Scrape the list of testcases of all questions

    def example_scrape(self):
        es = GetExampleList()
        es.scrape()  # Scrape the list of examples of all questions

    def start(self):
        # Call the function to launch
        self.question_list_scrape()
        self.get_description()
        self.test_scrape()
        self.example_scrape()
