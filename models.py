from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(100))

class Class(Base):
    __tablename__ = 'class'
    
    class_id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(50), nullable=False)
    class_code = Column(String(20), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Student(Base):
    __tablename__ = 'student'
    
    student_id = Column(String(20), primary_key=True)
    name = Column(String(50), nullable=False)
    class_id = Column(Integer, ForeignKey('class.class_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 添加与Class的关系
    class_ = relationship("Class", back_populates="students")

# 在Class模型中添加反向关系
Class.students = relationship("Student", back_populates="class_")

class Exam(Base):
    __tablename__ = 'exam'
    
    exam_id = Column(Integer, primary_key=True, autoincrement=True)
    exam_name = Column(String(100), nullable=False)
    answer_template = Column(Text)
    scoring_ratio = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class ExamScore(Base):
    __tablename__ = 'exam_score'
    
    score_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(20), ForeignKey('student.student_id'), nullable=False)
    exam_id = Column(Integer, ForeignKey('exam.exam_id'), nullable=False)
    subjective_score = Column(Float)
    objective_score = Column(Float)
    total_score = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 创建数据库连接
engine = create_engine('sqlite:///users.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine) 
