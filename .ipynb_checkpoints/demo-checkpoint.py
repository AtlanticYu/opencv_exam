
import numpy as np
import cv2
from sklearn.cluster import KMeans
from imutils.perspective import four_point_transform,order_points
import tornado.ioloop
import tornado.web
from tornado.web import StaticFileHandler
import tornado.options








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

    paper = four_point_transform(areas,box) ## 切出答题卡位置和透视变换\
    return paper  ## 返回A4纸所在的矩形框
    
    
    
def get_mask(image,value=0.8):
    """ 模板匹配 对准答案区域的四角"""
    template = cv2.imread("template.jpg")

    h, w = template.shape[:2]
    
    
    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
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


    paper = get_main_location_img(img,locations)
    paper1 = paper[0:1200,0:265]
    paper2 =  paper[0:1200,320:575]
    paper3 =  paper[0:1200,635:890]
    paper4 =  paper[0:1200,950:1215]
    paper = cv2.hconcat([paper1,paper2,paper3,paper4])
    print(paper.shape)

    plt.figure(figsize=(20,20))
    plt.imshow(paper)
    plt.show()

    # paper2 = paper[paper>=(220,220,220)]=255
    warped = cv2.cvtColor(paper, cv2.COLOR_BGR2GRAY) 
    as_data = []
    imgs= []

    for x_ in range(7):
        img3 = warped[1200-int(171*(7-x_))+10:int(171*(x_+1))-10,0:1025]

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
                as_data.append(a[ _data.index(min(_data))-1 ])
    return (as_data)

    


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        
        self.render("index.html")
        
    def post(self):
        img = Image.open(BytesIO(self.request.files['image'][0]['body']))
        img_rgb =  np.array(img)
        try:
            number = get_zkz(img_rgb)
            answer = get_da(img_rgb)
            self.write(json.dumps({"code":200,"number":number,"answer":answer}))
        except:
       
            self.write(json.dumps(
                {"code": 500, "msg":"识别出错!可能由于拍照不清楚造成!"
                }))
            return





def make_app():
    template_path = "templates/"
    static_path = "static/"

    return tornado.web.Application([
    
        (r"/", MainHandler),

    ], template_path=template_path, static_path=static_path, debug=True)


def run_server(port=8000):
    tornado.options.parse_command_line()
    app = make_app()
    app.listen(port)
    print("\n服务已启动 请打开 http://127.0.0.1:8000 ")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
   
    run_server()
    