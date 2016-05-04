#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask
app = Flask(__name__)

@app.route('/test')
def test():
    return "Hello !"

if __name__ == '__main__':
    app.run(debug=True)