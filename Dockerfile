FROM python:3.11.5

WORKDIR /home/aiogram-timetable

COPY config/ config/
COPY database/ database/
COPY handlers/ handlers/
COPY keyboards/ keyboards/
COPY middlewares/ middlewares/
COPY main.py main.py
COPY requirements.txt requirements.txt

RUN pip install --user -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["main.py"]