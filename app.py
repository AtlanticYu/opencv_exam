from tornado.web import RequestHandler, Application
from tornado.ioloop import IOLoop
from tornado.options import define, options
import os
import json
import tornado
from models import db, Class, Student, Exam, AnswerSheet, Score
from datetime import datetime

define("port", default=8888, help="run on the given port", type=int)

class BaseHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    def get(self):
        self.render("index.html")

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")
    
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        # 这里应该添加实际的用户验证逻辑
        if username and password:
            self.set_secure_cookie("user", username)
            self.write({"code": 0, "msg": "登录成功"})
        else:
            self.write({"code": 1, "msg": "用户名或密码不能为空"})

class ClassManageHandler(BaseHandler):
    def get(self):
        self.render("class_manage.html")

class ClassAddHandler(BaseHandler):
    def get(self):
        self.render("class_add.html")

class ClassListAPIHandler(BaseHandler):
    def get(self):
        classes = db.query(Class).all()
        data = [{
            "class_id": c.class_id,
            "class_name": c.class_name,
            "class_code": c.class_code,
            "student_count": len(c.students),
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for c in classes]
        self.write({"code": 0, "data": data})

class ClassAddAPIHandler(BaseHandler):
    def post(self):
        class_name = self.get_argument("class_name")
        class_code = self.get_argument("class_code")
        new_class = Class(class_name=class_name, class_code=class_code)
        db.add(new_class)
        db.commit()
        self.write({"code": 0, "msg": "添加成功"})

class ClassDeleteAPIHandler(BaseHandler):
    def post(self):
        class_id = self.get_argument("class_id")
        db.query(Class).filter(Class.class_id == class_id).delete()
        db.commit()
        self.write({"code": 0, "msg": "删除成功"})

class StudentManageHandler(BaseHandler):
    def get(self):
        self.render("student_manage.html")

class StudentAddHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("student_add.html")
    
    @tornado.web.authenticated
    def post(self):
        try:
            # 获取必填字段
            class_id = self.get_argument("class_id")
            student_id = self.get_argument("student_id")
            name = self.get_argument("name")
            
            # 检查学号是否已存在
            existing_student = db.query(Student).filter(Student.student_id == student_id).first()
            if existing_student:
                self.write({"code": 1, "msg": "该学号已存在"})
                return
            
            # 创建新学生
            new_student = Student(
                class_id=class_id,
                student_id=student_id,
                name=name,
            )
            
            # 保存到数据库
            db.add(new_student)
            db.commit()
            
            self.write({"code": 0, "msg": "添加成功"})
        except Exception as e:
            db.rollback()
            self.write({"code": 1, "msg": f"添加失败：{str(e)}"})

class StudentListAPIHandler(BaseHandler):
    def get(self):
        students = db.query(Student).all()
        data = [{
            "student_id": s.student_id,
            "name": s.name,
            "class_name": s.class_.class_name,
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for s in students]
        self.write({"code": 0, "data": data})

class StudentDeleteAPIHandler(BaseHandler):
    def post(self):
        student_id = self.get_argument("student_id")
        db.query(Student).filter(Student.student_id == student_id).delete()
        db.commit()
        self.write({"code": 0, "msg": "删除成功"})

class StudentAddAPIHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            # 获取必填字段
            class_id = self.get_argument("class_id")
            student_id = self.get_argument("student_id")
            name = self.get_argument("name")
            
            # 检查学号是否已存在
            existing_student = db.query(Student).filter(Student.student_id == student_id).first()
            if existing_student:
                self.write({"code": 1, "msg": "该学号已存在"})
                return
            
            # 创建新学生
            new_student = Student(
                class_id=class_id,
                student_id=student_id,
                name=name,
            )
            
            # 保存到数据库
            db.add(new_student)
            db.commit()
            
            self.write({"code": 0, "msg": "添加成功"})
        except Exception as e:
            db.rollback()
            self.write({"code": 1, "msg": f"添加失败：{str(e)}"})

def make_app():
    return Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/class/manage", ClassManageHandler),
        (r"/class/add", ClassAddHandler),
        (r"/api/class/list", ClassListAPIHandler),
        (r"/api/class/add", ClassAddAPIHandler),
        (r"/api/class/delete", ClassDeleteAPIHandler),
        (r"/student/manage", StudentManageHandler),
        (r"/student/add", StudentAddHandler),
        (r"/api/student/list", StudentListAPIHandler),
        (r"/api/student/add", StudentAddAPIHandler),
        (r"/api/student/delete", StudentDeleteAPIHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static")}),
    ],
    cookie_secret="your-secret-key",
    login_url="/login",
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    debug=True)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = make_app()
    app.listen(options.port)
    IOLoop.current().start() 