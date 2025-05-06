from models import Base, engine

def recreate_tables():
    # 删除所有表
    Base.metadata.drop_all(engine)
    # 重新创建所有表
    Base.metadata.create_all(engine)
    print("数据库表已重新创建")

if __name__ == "__main__":
    recreate_tables() 