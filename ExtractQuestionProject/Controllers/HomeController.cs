using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using ExtractQuestionProject.Models;
using System.Data;

namespace ExtractQuestionProject.Controllers
{
    public class HomeController : Controller
    {
        public ActionResult Index()
        {
            return View();
        }

        public ActionResult About()
        {
            ViewBag.Message = "Your application description page.";

            return View();
        }

        public ActionResult Contact()
        {
            ViewBag.Message = "Your contact page.";

            return View();
        }

        public ActionResult Main()
        {
            Session["Name"] = "Master";
            Session["Empcode"] = "M001";
            return View();
        }


        [HttpPost]
        public ActionResult FetchTODOAllData()
        {
            String Message = "", Status = "Error";
            if (HttpContext.Session["Empcode"].ToString() == null)
            {
                Message = "Sorry! Session Expired. Login Again ..";
                Status = "Error";
                return Json(new { Message = Message, Status = Status });
            }
            List<Param1> list = new List<Param1>();
            try
            {
                DataTable dt = ExecuteMe.Select(QuerySet.selectMain, "Demo");
                for (int i = 0; i < dt.Rows.Count; i++)
                {
                    list.Add(new Param1
                    {
                        QuestionLink = dt.Rows[i]["OriginalLink"].ToString(),
                        QuestionName = dt.Rows[i]["Title"].ToString(),
                    });
                }
            }
            catch (Exception e)
            {
                Message = "Record does not added due to above exception";
                Status = "Error";
                return Json(new { Message = Message, Status = Status });
            }

            return Json(list, JsonRequestBehavior.AllowGet);
        }
        public ActionResult FetchTODOQuestionData(Param1 user)
        {
            String Message = "", Status = "Error";
            if (HttpContext.Session["Empcode"].ToString() == null)
            {
                Message = "Sorry! Session Expired. Login Again ..";
                Status = "Error";
                return Json(new { Message = Message, Status = Status });
            }
            List<Param1> list = new List<Param1>();
            try
            {
                DataTable dt = ExecuteMe.Select(QuerySet.selectQuestion + $"WHERE OriginalLink = '{user.QuestionLink}';", "Demo");
                list.Add(new Param1
                    {
                        QuestionName = dt.Rows[0]["Title"].ToString(),
                        Description = dt.Rows[0]["Question"].ToString(),
                        QuestionId = dt.Rows[0]["Question_ID"].ToString()
                });

            }
            catch (Exception e)
            {
                Message = "Record does not added due to above exception";
                Status = "Error";
                return Json(new { Message = Message, Status = Status });
            }

            return Json(list, JsonRequestBehavior.AllowGet);
        }

        public ActionResult FetchTODOExampleData(Param1 user)
        {
            String Message = "", Status = "Error";
            if (HttpContext.Session["Empcode"].ToString() == null)
            {
                Message = "Sorry! Session Expired. Login Again ..";
                Status = "Error";
                return Json(new { Message = Message, Status = Status });
            }
            List<Param1> list = new List<Param1>();
            try
            {
                DataTable dt = ExecuteMe.Select(QuerySet.selectQuestion + $"WHERE Question_ID = '{user.QuestionId}';", "Demo");
                for (int i = 0; i < dt.Rows.Count; i++)
                {

                    list.Add(new Param1
                    {
                        Input = dt.Rows[0]["Title"].ToString(),
                        Output = dt.Rows[0]["Question"].ToString(),
                        Explaination = dt.Rows[0]["Question"].ToString(),
                    });
                }
            }
            catch (Exception e)
            {
                Message = "Record does not added due to above exception";
                Status = "Error";
                return Json(new { Message = Message, Status = Status });
            }

            return Json(list, JsonRequestBehavior.AllowGet);
        }
    }
}