using MySqlConnector;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Web;

namespace ExtractQuestionProject.Models
{
    public class ExecuteMe
    {
        public static MySqlConnection MyConnectionString(string type)
        {
            MySqlConnection m = new MySqlConnection();
            if (type == "Demo")
            {
                m.ConnectionString = ConfigurationManager.ConnectionStrings["Demo"].ConnectionString;
            }
            if (type == "Convo")
            {
                m.ConnectionString = ConfigurationManager.ConnectionStrings["convo"].ConnectionString;
            }
            return m;
        }
        public static DataTable Select(string query, string connectionName)
        {
            MySqlDataAdapter da2 = new MySqlDataAdapter(query, MyConnectionString(connectionName));
            DataTable dt2 = new DataTable();
            da2.Fill(dt2);
            return dt2;
        }
        public static int DeleteInsertUpdate(string query, string connectionName)
        {
            MySqlDataAdapter da2 = new MySqlDataAdapter(query, MyConnectionString(connectionName));
            DataTable dt2 = new DataTable();
            int res = da2.Fill(dt2);
            return res;

        }
    }
}