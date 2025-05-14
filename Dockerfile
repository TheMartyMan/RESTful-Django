FROM python:3.13.1-slim


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /Excercize
COPY . /Excercize/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


EXPOSE 8001

CMD ["gunicorn", "--chdir", "/Excercize", "Excercize.wsgi:application", "--bind", "0.0.0.0:8001"]