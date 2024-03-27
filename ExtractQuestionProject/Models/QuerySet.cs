using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace ExtractQuestionProject.Models
{
    public class QuerySet
    {
        public const String selectMain = "SELECT * FROM question_master_coding";
        public const String selectQuestion = "SELECT Title, Question, Question_ID FROM question_master_coding ";
        public const String selectExample = "SELECT * FROM question_master_detail_coding ";

    }
}