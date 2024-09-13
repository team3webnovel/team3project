import cx_Oracle
import os
import logging
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 데이터베이스 URL 설정 (SQLAlchemy 사용)
DATABASE_URL = "oracle+cx_oracle://Team3_project:T3Proj#Secure@adb.ap-chuncheon-1.oraclecloud.com:1522/?service_name=g699a7358c7003f_obdehifxdix5mjdt_high.adb.oraclecloud.com"

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 세션 로컬 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def open_db_connection():
    """DB에 연결하는 함수"""
    log_filename = 'db_connection_log.txt'
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler(log_filename, encoding='utf-8'),
                            logging.StreamHandler(sys.stdout)
                        ])

    wallet_dir = r'C:\app\201-29\product\instantclient-basic-windows.x64-23.5.0.24.07\instantclient_23_5\network\admin\Wallet_OBDEHIFXDIX5MJDT'

    if not os.path.exists(wallet_dir):
        logging.error(f"오라클 지갑 경로가 존재하지 않습니다: {wallet_dir}")
        return None

    os.environ['TNS_ADMIN'] = wallet_dir

    dsn = "obdehifxdix5mjdt_high"
    username = "Team3_project"
    password = "T3Proj#Secure"

    try:
        logging.info(f"데이터베이스 연결 시도 중... TNS_ADMIN 경로: {os.environ['TNS_ADMIN']}")
        connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        logging.info("DB 연결 성공")
        return connection

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        logging.error(f"DB 연결 또는 쿼리 실행 중 오류 발생: {error.message}")
        return None

    except Exception as ex:
        logging.error(f"알 수 없는 오류 발생: {str(ex)}")
        return None


def open_db_session():
    """
    SQLAlchemy 세션을 열고 DB 연결 객체를 반환하는 함수.
    이 함수는 DB 연결 및 세션을 열고 요청마다 세션을 반환한 후 닫습니다.
    """
    connection = open_db_connection()  # cx_Oracle 연결

    if connection:
        session = SessionLocal()  # SQLAlchemy 세션 생성
        try:
            yield session
        finally:
            session.close()
            connection.close()
            logging.info("DB 세션 및 연결 종료")
    else:
        logging.error("DB 연결을 열 수 없습니다.")


# 앱 종료 시 호출되는 함수
def shutdown_db_connection():
    engine.dispose()
    logging.info("DB 연결이 종료되었습니다.")


# 테스트 용도로 DB 연결 확인
def connect_to_db():
    """테스트용 DB 연결 및 쿼리 실행 함수"""
    connection = open_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchone()
            logging.info(f"쿼리 실행 성공, 결과: {result}")
            print(f"쿼리 실행 성공, 결과: {result}")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            logging.error(f"쿼리 실행 중 오류 발생: {error.message}")
        finally:
            cursor.close()
            connection.close()
            logging.info("DB 연결 종료")
    else:
        logging.error("DB 연결을 열 수 없습니다.")

if __name__ == "__main__":
    connect_to_db()
