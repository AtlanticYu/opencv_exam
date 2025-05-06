-- 创建用户表
CREATE TABLE users (
    id INTEGER NOT NULL PRIMARY KEY, -- 用户ID，主键
    username VARCHAR(50) UNIQUE, -- 用户名，唯一
    password VARCHAR(100) -- 密码
);

-- 创建班级表
CREATE TABLE class (
    class_id INT PRIMARY KEY AUTO_INCREMENT, -- 班级ID，主键，自增
    class_name VARCHAR(50) NOT NULL, -- 班级名称
    class_code VARCHAR(20) NOT NULL UNIQUE, -- 班级编号，唯一
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- 更新时间
);

-- 创建学生表
CREATE TABLE student (
    student_id INT PRIMARY KEY AUTO_INCREMENT, -- 学生ID，主键，自增
    student_name VARCHAR(50) NOT NULL, -- 学生姓名
    exam_number VARCHAR(20) NOT NULL UNIQUE, -- 准考证号，唯一
    class_id INT NOT NULL, -- 所属班级ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- 更新时间
);

-- 创建考试表
CREATE TABLE exam (
    exam_id INT PRIMARY KEY AUTO_INCREMENT, -- 考试ID，主键，自增
    exam_name VARCHAR(100) NOT NULL, -- 考试名称
    answer_template TEXT, -- 答题卡模板
    scoring_ratio VARCHAR(100) NOT NULL, -- 赋分比例
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- 更新时间
);

-- 创建考试成绩表
CREATE TABLE exam_score (
    score_id INT PRIMARY KEY AUTO_INCREMENT, -- 成绩ID，主键，自增
    student_id INT NOT NULL, -- 学生ID
    exam_id INT NOT NULL, -- 考试ID
    subjective_score DECIMAL(5,2), -- 主观题成绩
    objective_score DECIMAL(5,2), -- 客观题成绩
    total_score DECIMAL(5,2), -- 总分
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- 更新时间
); 