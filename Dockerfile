FROM ubi8/python-39
LABEL maintainer="tbrunell@redhat.com"
USER 0

RUN yum -y install opencv-core opencv-contrib

RUN python3 -m pip install --upgrade pip 
WORKDIR /app
RUN pip3 install mediapipe
RUN pip3 install matplotlib
RUN pip3 install flask

EXPOSE 8080

COPY . /app
ENTRYPOINT ["python3"]
CMD ["app.py"]
