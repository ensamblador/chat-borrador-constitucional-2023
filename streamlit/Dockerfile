FROM python:3.9-slim
WORKDIR /app
ADD *.*  /app
RUN pip3 install -r requirements.txt 
RUN aws s3 sync s3://constitucionchat-streamlitbucket2fe9c216-37ik5ijjfnl3/streamlit/ .
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "chatbot_app.py", "--server.port=8501"]