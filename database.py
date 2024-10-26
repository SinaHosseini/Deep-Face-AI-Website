from sqlmodel import SQLModel, Field, Session, select, create_engine


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    first_name: str = Field()
    last_name: str = Field()
    email: str = Field()
    username: str = Field()
    age: int = Field()
    country: str = Field()
    city: str = Field()
    password: str = Field()
    join_time: str = Field()


engine = create_engine("sqlite:///./database.db", echo=True)
SQLModel.metadata.create_all(engine)


def get_user_by_username(username: str):
    with Session(engine) as db_session:
        statement = select(User).where(User.username == username)
        
        return db_session.exec(statement).first()


def create_user(first_name: str, last_name: str, email: str, username: str, age: int, country: str, city: str, password: str, confirm_password: str, join_time: str):
    user = User(first_name = first_name, last_name = last_name, email = email, username = user, age = age, country = country, city = city, password = password, confirm_password = confirm_password, join_time = join_time)
    with Session(engine) as db_session:
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        return user
    
    