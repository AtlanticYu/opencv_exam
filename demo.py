import numpy as np
import cv2
from sklearn.cluster import KMeans
from imutils.perspective import four_point_transform,order_points
import tornado.ioloop
import matplotlib.pyplot as plt
import tornado.web
from tornado.web import StaticFileHandler
import tornado.options
from PIL import Image
import base64,json
import traceback
from io import BytesIO
from models import Session, User, Class, Student, Exam, ExamScore
import hashlib
from datetime import datetime






def get_zkz(img_rgb):
    """传入 RGB的图片数组 获取准考证"""

    template = cv2.imread("A.jpg")
    template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
    h, w = template.shape[:2]

    # img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)


    # 2.标准相关模板匹配
    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.25

    # 3.这边是Python/Numpy的知识，后面解释
    loc = np.where(res >= threshold)  # 匹配程度大于%80的坐标y,x
    y,x = int(np.median(loc[0]))-180, int(np.median(loc[1]))-100
    print(x,y)
    right_bottom = (x + w+160, y + h+300)
    # cv2.rectangle(img_rgb, (x,y), right_bottom, (255,0, 0), 2)


    areas = img_rgb[y:y+h+300,x:x+w+160]

    

    marker = cv2.resize(find_marker(areas),(430,590))[150:590,0:430]
    print(marker.shape)

    number = []
    for _x in range(11):
        img2 = marker[0:440,int(39*_x):int(39*(_x+1))]
        img3 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        thresh=cv2.adaptiveThreshold(img3,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,53,20)
        ChQImg = cv2.blur(thresh, (20,20))
        #二进制二值化
        ChQImg = cv2.threshold(ChQImg, 100, 180, cv2.THRESH_BINARY)[1]
        _data =[]
        a = list(range(10))
        for x_ in range(10): 
            img4 = img3[int(44*x_):int(44*(x_+1)),0:430]
            _data.append(np.sum(img4))

        else:
            number.append(a[ _data.index(min(_data)) ])
    return number


def find_marker(Img):
    """ 使用 白色限定过滤掉其他多余的颜色 使得A4纸检测更加准确"""

    if Img is not None:#判断图片是否读入
#         
        mask = cv2.cvtColor(Img, cv2.COLOR_BGR2GRAY)
        Lower = np.array([20,30,30])#要识别白色颜色的下限
        Upper = np.array([ 230, 180, 180])#要识别白色颜色的上限
        #mask是把HSV图片中在颜色范围内的区域变成白色，其他区域变成黑色
        mask = cv2.inRange(Img, Lower, Upper)

        ret, binary = cv2.threshold(mask,170,200,cv2.THRESH_BINARY)
        #在binary中发现轮廓，轮廓按照面积从小到大排列
        ( cnts, _)= cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        if cnts==[]:
           return 0

    c= max(cnts, key = cv2.contourArea)
    rect = cv2.minAreaRect(c)
    box = cv2.boxPoints(rect)
    print(box)

    paper = four_point_transform(Img,box) ## 切出答题卡位置和透视变换\
    return paper  ## 返回A4纸所在的矩形框
    
    
    
def get_mask(image,value=0.8):
    """ 模板匹配 对准答案区域的四角"""
    template = cv2.imread("template.jpg")

    h, w = template.shape[:2]
    
    
    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    threshold = value
    loc = np.where(res >= threshold)  # 匹配程度大于%80的坐标y,x
    
    locations = []
    
    for pt in zip(*loc[::-1]):  # *号表示可选参数
        locations.append(pt)
    return locations





def get_main_location_img(img,locations):
    
    """ 使用 K-means聚类进行聚类坐标集"""
    estimator = KMeans(n_clusters=4)#构造聚类器
    estimator.fit(locations)#聚类
    centroids = estimator.cluster_centers_ #获取聚类中心
    centroids = order_points(centroids) ## 坐标点排序



    centroids = np.array([[centroids[0][0]-20,centroids[0][1]+17],
                          [centroids[1][0]+80,centroids[1][1]+17],
                          [centroids[2][0]+80,centroids[2][1]-25],
                          [centroids[3][0]-20,centroids[3][1]-25]])  ## 坐标偏移 回归正位






    paper = four_point_transform(img,centroids) ## 切出答题卡位置和透视变换\
    paper = cv2.resize(paper,(1200,1200))
    return paper




def get_da(img_rgb):
    """传入 RGB的图片数组 获取答案"""

    locations = get_mask(img_rgb)    


    paper = get_main_location_img(img_rgb,locations)
    paper1 = paper[0:1200,0:265]
    paper2 =  paper[0:1200,320:575]
    paper3 =  paper[0:1200,635:890]
    paper4 =  paper[0:1200,950:1215]
    paper = cv2.hconcat([paper1,paper2,paper3,paper4])
    print(paper.shape)

    # plt.figure(figsize=(20,20))
    # plt.imshow(paper)
    # plt.show()

    # paper2 = paper[paper>=(220,220,220)]=255
    warped = cv2.cvtColor(paper, cv2.COLOR_BGR2GRAY) 
    as_data = []
    imgs= []

    for x_ in range(7):
        img3 = warped[1200-int(171*(7-x_))+10:int(171*(x_+1))-10,0:1025]
        v_data = []
        for _x in range(20):
        #     plt.subplot(1,18,x)


            img4 =img3[0:171,int(51.25*(_x)):int(51.25*(_x+1))] 
            for x in range(img4.shape[0]):
                ol=sum(list(img4[x]))

                if ol<10577:
                    break
            h,w = img4.shape
            img5 = img4[x:h,0:w]
            thresh=cv2.adaptiveThreshold(img4,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,53,20)
            ChQImg = cv2.blur(thresh, (20,20))
            #二进制二值化
            ChQImg = cv2.threshold(ChQImg, 100, 180, cv2.THRESH_BINARY)[1]
        #     print(ChQImg)
        #     plt.imshow(ChQImg)
        #     plt.show()
        #     ChQImg[ChQImg==180]=0
            a= ["A","B","C","D"]
            _data =[]
            for z in range(5):
                _data.append(np.sum(ChQImg[int(29*z):int(29*(z+1)),0:50]))
            else:
                
                v_data.append(a[ _data.index(min(_data))-1 ])
        as_data.append(v_data)
    return (as_data)
import os
if os.path.exists("right_as.json"):
    right_as = json.load(open("right_as.json"))
else:
    right_as = {}

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html")
        
    def post(self):
        try:
            username = self.get_argument("username")
            password = self.get_argument("password")
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            
            session = Session()
            user = session.query(User).filter_by(username=username).first()
            
            if user:
                if user.password == hashed_password:
                    self.set_secure_cookie("user", username)
                    self.write(json.dumps({"code": 200, "msg": "登录成功"}))
                else:
                    self.write(json.dumps({"code": 400, "msg": "密码错误"}))
            else:
                # 创建新用户
                new_user = User(username=username, password=hashed_password)
                session.add(new_user)
                session.commit()
                self.set_secure_cookie("user", username)
                self.write(json.dumps({"code": 200, "msg": "新用户创建成功"}))
            
            session.close()
        except Exception as e:
            print(f"Login error: {str(e)}")
            self.write(json.dumps({"code": 500, "msg": "服务器错误"}))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("user"):
            self.redirect("/login")
            return
        self.render("index.html")
        
    def post(self):
        if not self.get_secure_cookie("user"):
            self.write(json.dumps({"code": 401, "msg": "请先登录"}))
            return
            
        if self.get_argument("method") =="com":
            img = Image.open(BytesIO(self.request.files['image'][0]['body']))
            img_rgb =  np.array(img)
            try:
                number = get_zkz(img_rgb)
                answer = get_da(img_rgb)
                error = 0
                # answer = [{str(i):"第"+str(i+e*20+1)+"题"+v for i,v in enumerate(target_list)} for e,target_list in enumerate(answer) ]
                answer_com = []
                for e,x in  enumerate(answer):
                    for i,v in enumerate(x):
                        if right_as[str(i+e*20+1)] != v:
                            error+=1
                     

                answer = [{str(i):"第"+str(i+e*20+1)+"题"+v for i,v in enumerate(target_list)} for e,target_list in enumerate(answer) ]

                self.write(json.dumps({"code":200,"number":number,"answer":answer,"error":error}))
            except:
                print(traceback.format_exc())
                self.write(json.dumps(
                    {"code": 500, "msg":"识别出错!可能由于拍照不清楚造成!"
                    }))
                return
        else:
            img = Image.open(BytesIO(self.request.files['image'][0]['body']))
            img_rgb =  np.array(img)
            try:
                number = get_zkz(img_rgb)
                answer = get_da(img_rgb)
                # answer = [{str(i):"第"+str(i+e*20+1)+"题"+v for i,v in enumerate(target_list)} for e,target_list in enumerate(answer) ]

                for e,x in  enumerate(answer):
                    for i,v in enumerate(x):
                        right_as[str(i+e*20+1)] = v
                json.dump(right_as,open("right_as.json","w"))


                self.write(json.dumps({"code":500,"msg":"设置完成!"}))
            except:
                print(traceback.format_exc())
                self.write(json.dumps(
                    {"code": 500, "msg":"识别出错!可能由于拍照不清楚造成!"
                    }))
                return

class UserInfoHandler(tornado.web.RequestHandler):
    def get(self):
        username = self.get_secure_cookie("user")
        if username:
            self.write(json.dumps({"code": 200, "username": username.decode()}))
        else:
            self.write(json.dumps({"code": 401, "msg": "未登录"}))

class ClassManageHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("user"):
            self.redirect("/login")
            return
        self.render("class_manage.html")

class ClassAddHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("user"):
            self.redirect("/login")
            return
        self.render("class_add.html")

class ClassListHandler(tornado.web.RequestHandler):
    def get(self):
        session = Session()
        try:
            # 获取分页参数
            page = int(self.get_argument('page', 1))
            limit = int(self.get_argument('limit', 10))
            
            # 计算偏移量
            offset = (page - 1) * limit
            
            # 查询班级列表
            classes = session.query(Class).offset(offset).limit(limit).all()
            total = session.query(Class).count()
            
            result = []
            for c in classes:
                student_count = session.query(Student).filter_by(class_id=c.class_id).count()
                result.append({
                    'class_id': c.class_id,
                    'class_name': c.class_name,
                    'class_code': c.class_code,
                    'student_count': student_count,
                    'created_at': c.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            self.write(json.dumps({
                "code": 0,
                "msg": "success",
                "count": total,
                "data": result
            }))
        except Exception as e:
            self.write(json.dumps({
                "code": 1,
                "msg": str(e)
            }))
        finally:
            session.close()

class ClassAddApiHandler(tornado.web.RequestHandler):
    def post(self):
        session = Session()
        try:
            class_name = self.get_argument("class_name")
            class_code = self.get_argument("class_code")
            
            # 检查班级编号是否已存在
            existing = session.query(Class).filter_by(class_code=class_code).first()
            if existing:
                self.write(json.dumps({"code": 400, "msg": "班级编号已存在"}))
                return
            
            new_class = Class(
                class_name=class_name,
                class_code=class_code
            )
            session.add(new_class)
            session.commit()
            self.write(json.dumps({"code": 200, "msg": "添加成功"}))
        except Exception as e:
            session.rollback()
            self.write(json.dumps({"code": 500, "msg": str(e)}))
        finally:
            session.close()

class ClassDeleteHandler(tornado.web.RequestHandler):
    def post(self):
        session = Session()
        try:
            class_id = self.get_argument("class_id")
            
            # 检查是否有学生
            student_count = session.query(Student).filter_by(class_id=class_id).count()
            if student_count > 0:
                self.write(json.dumps({"code": 400, "msg": "班级中还有学生，无法删除"}))
                return
            
            class_obj = session.query(Class).filter_by(class_id=class_id).first()
            if class_obj:
                session.delete(class_obj)
                session.commit()
                self.write(json.dumps({"code": 200, "msg": "删除成功"}))
            else:
                self.write(json.dumps({"code": 404, "msg": "班级不存在"}))
        except Exception as e:
            session.rollback()
            self.write(json.dumps({"code": 500, "msg": str(e)}))
        finally:
            session.close()

class StudentManageHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("user"):
            self.redirect("/login")
            return
        self.render("student_manage.html")

class StudentListHandler(tornado.web.RequestHandler):
    def get(self):
        session = Session()
        try:
            # 获取分页参数
            page = int(self.get_argument('page', 1))
            limit = int(self.get_argument('limit', 10))
            
            # 计算偏移量
            offset = (page - 1) * limit
            
            # 查询学生列表
            students = session.query(Student, Class).join(Class, Student.class_id == Class.class_id)\
                .offset(offset).limit(limit).all()
            total = session.query(Student).count()
            
            result = []
            for student, cls in students:
                result.append({
                    'student_id': student.student_id,
                    'name': student.name,
                    'class_name': cls.class_name,
                    'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
                
            self.write(json.dumps({
                "code": 0,
                "msg": "success",
                "count": total,
                "data": result
            }))
        except Exception as e:
            self.write(json.dumps({
                "code": 1,
                "msg": str(e)
            }))
        finally:
            session.close()

class StudentAddHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("user"):
            self.redirect("/login")
            return
        self.render("student_add.html")
    
    def post(self):
        if not self.get_secure_cookie("user"):
            self.write(json.dumps({"code": 401, "msg": "请先登录"}))
            return
            
        try:
            # 获取必填字段
            class_id = self.get_argument("class_id")
            student_id = self.get_argument("student_id")
            name = self.get_argument("name")
            
            # 检查学号是否已存在
            session = Session()
            existing_student = session.query(Student).filter(Student.student_id == student_id).first()
            if existing_student:
                self.write(json.dumps({"code": 1, "msg": "该学号已存在"}))
                session.close()
                return

            
            # 创建新学生
            new_student = Student(
                class_id=class_id,
                student_id=student_id,
                name=name,
            )
            
            # 保存到数据库
            session.add(new_student)
            session.commit()
            session.close()
            
            self.write(json.dumps({"code": 0, "msg": "添加成功"}))
        except Exception as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            self.write(json.dumps({"code": 1, "msg": f"添加失败：{str(e)}"}))

class StudentAddAPIHandler(tornado.web.RequestHandler):
    def post(self):
        session = Session()
        try:
            # 获取参数
            student_id = self.get_argument("student_id", "").strip()
            name = self.get_argument("name", "").strip()
            class_id = self.get_argument("class_id", "").strip()

            # 校验参数
            if not student_id or not name or not class_id:
                self.write({"code": 400, "msg": "学号、姓名、班级不能为空"})
                return

            # 检查学号是否已存在
            existing = session.query(Student).filter_by(student_id=student_id).first()
            if existing:
                self.write({"code": 400, "msg": "学号已存在"})
                return

            # 检查班级是否存在
            class_obj = session.query(Class).filter_by(class_id=class_id).first()
            if not class_obj:
                self.write({"code": 400, "msg": "班级不存在"})
                return

            # 创建新学生
            new_student = Student(
                student_id=student_id,
                name=name,
                class_id=class_id
            )
            session.add(new_student)
            session.commit()
            self.write({"code": 200, "msg": "添加成功"})
        except Exception as e:
            session.rollback()
            self.write({"code": 500, "msg": f"添加失败: {str(e)}"})
        finally:
            session.close()

class StudentDeleteHandler(tornado.web.RequestHandler):
    def post(self):
        session = Session()
        try:
            student_id = self.get_argument("student_id")
            
            # 检查是否有考试成绩
            score_count = session.query(ExamScore).filter_by(student_id=student_id).count()
            if score_count > 0:
                self.write(json.dumps({"code": 1, "msg": "该学生有考试成绩记录，无法删除"}))
                return
            
            student = session.query(Student).filter_by(student_id=student_id).first()
            if student:
                session.delete(student)
                session.commit()
                self.write(json.dumps({"code": 0, "msg": "删除成功"}))
            else:
                self.write(json.dumps({"code": 1, "msg": "学生不存在"}))
        except Exception as e:
            session.rollback()
            self.write(json.dumps({"code": 1, "msg": str(e)}))
        finally:
            session.close()

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/user/info", UserInfoHandler),
        (r"/class/manage", ClassManageHandler),
        (r"/class/add", ClassAddHandler),
        (r"/api/class/list", ClassListHandler),
        (r"/api/class/add", ClassAddApiHandler),
        (r"/api/class/delete", ClassDeleteHandler),
        (r"/student/manage", StudentManageHandler),
        (r"/student/add", StudentAddHandler),
        (r"/api/student/list", StudentListHandler),
        (r"/api/student/add", StudentAddAPIHandler),
        (r"/api/student/delete", StudentDeleteHandler),
        (r"/static/(.*)", StaticFileHandler, {"path": "static"}),
    ], 
    template_path="templates",
    static_path="static",
    cookie_secret="your-cookie-secret-here",
    debug=True)

def run_server(port=8000):
    tornado.options.parse_command_line()
    app = make_app()
    app.listen(port)
    print(f"Server started on port {port}")
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    run_server()
    