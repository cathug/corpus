from sqlalchemy import create_engine, Column, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB, BYTEA
from sqlalchemy.types import Integer, LargeBinary, TIMESTAMP, VARCHAR

# init database engine and declare mapping
engine = create_engine(
    'postgresql://csrp:csrp0000@localhost:5432/csrp', echo=True)
Base = declarative_base()


# Cataloging tables in base using the following Python classes
class AV_Images(Base):
    __tablename__ = 'av_images'

    avi_id = Column(Integer, Sequence('avi_id_seq'), primary_key=True)
    aviblob = Column(LargeBinary)
    filetype = Column(VARCHAR(length=255, convert_unicode=True))


class LIHKGScrapes(Base):
    __tablename__ = 'lihkg_json'

    lihkg_id = Column(Integer, Sequence('lihkg_json_id_seq'), primary_key=True)
    json_binary = Column(JSONB)

    # leave one byte for null character
    topic = Column(VARCHAR(length=255, convert_unicode=True))
    file_name = Column(VARCHAR(length=255, convert_unicode=True))
    last_reply_date = Column(TIMESTAMP(timezone=True))
    emfile_name = Column(VARCHAR(length=255, convert_unicode=True))



class HKGScrapes(Base):
    __tablename__ = 'hkg_json'

    hkg_id = Column(Integer, Sequence('hkg_json_id_seq'), primary_key=True)
    json_binary = Column(JSONB)

    # leave one byte for null character
    topic = Column(VARCHAR(length=255, convert_unicode=True) )
    file_name = Column(VARCHAR(length=255, convert_unicode=True))
    last_reply_date = Column(TIMESTAMP(timezone=True))


def main():

    # Session = sessionmaker(bind=engine) # bind engine to sessionmaker
    # session = Session() # init session
    Base.metadata.create_all(engine) # create table
    #
    # # CRUD operations
    #
    # # insert
    # newfile = AV_Images(
    #     title='',
    #     avi_id='',
    #     sha1_digest='',
    #     aviblob='',
    #     filetype=''
    # )
    #
    # session.add()
    # session.commit()
    #

    # def main():
    #     db = Database(db_name='csrp', db_user='csrp', user_password='csrp0000')
    #     db.checkPostgreSQLVersion()
    #


if __name__ == '__main__':
    main()
