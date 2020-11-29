from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

'''
安装步骤
easy_install -U pip
pip install flask-sqlalchemy
pip install flask-mysqldb
pip install flask-wtf
'''
# print('The __name__ = ' + __name__)
__name__ = 'main'
print(__name__)

app = Flask(__name__)

# 数据库配置
# 需要自己创建flask_book_project
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@127.0.0.1/flask_book_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['debug'] = True
app.secret_key = 'abcd1234'
db = SQLAlchemy(app)


# 创建Model
class Author(db.Model):
    __tablename__ = 'Authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    books = db.relationship('Book', backref='Author')

    def _repr(self):
        return 'Author <id:%s, name:%s>' % (self.id, self.name)


class Book(db.Model):
    __tablename__ = 'Books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    author = db.Column(db.Integer, db.ForeignKey('Authors.id'))


# 添加数据
db.drop_all()
db.create_all()
author1 = Author(name='王升平')
author2 = Author(name='王韫昕')
author3 = Author(name='张凤')
db.session.add_all([author1, author2, author3])
db.session.commit()

book1 = Book(name='老王回忆录2', author=author1.id)
book2 = Book(name='我读书少，别骗我', author=author1.id)
book3 = Book(name='如何成功', author=author2.id)
book4 = Book(name='穷爸爸、富爸爸', author=author3.id)
book5 = Book(name='Java 教程', author=author3.id)
db.session.add_all([book1, book2, book3, book4, book5])
db.session.commit()

'''
1. 配置数据库
2. 定义模型
    - 模型继承db.Model
    - db.relationship
3. 添加数据
4. 显示数据
5. WTF显示表单
6. 实现相关增删逻辑
'''

# 自定义表单类
class AuthForm(FlaskForm):
    author = StringField('作者', validators=[DataRequired()])
    book = StringField('书籍', validators=[DataRequired()])
    submit = SubmitField('添加书籍  ')

@app.route('/', methods=['GET','POST'])
def index():
    # 创建自定义表单类
    author_form = AuthForm()
    '''
    验证逻辑
    1. 调用WTF的函数实现验证
    2. 验证通过获取数据    
    '''

    if author_form.validate_on_submit():
        author_name = author_form.author.data
        book_name = author_form.book.data

        # 判断作者是否存在
        author = Author.query.filter_by(name=author_name).first()
        if author:
            book = Book.query.filter_by(name=book_name).first()
            if book:
                flash('已经存在同名书籍')
            else:
                try:
                    new_book = Book(name=book_name, author=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    flash('添加书籍失败')
                    db.session.rollback()
                pass
            pass
        else:
            try:
                # 添加作者
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()

                new_book = Book(name=book_name, author=new_author.id)
                db.session.add(new_book)
                db.session.commit()
                pass
            except Exception as e:
                print(e)
                flash('添加作者、书籍报错')
                db.session.rollback()
            pass
        pass
    else:
        if request.method == 'POST':
            flash('参数不全')

    # 查询所有作者的信息，让信息传递给作者
    print("query all the authors")
    authors = Author.query.all()
    return render_template('books.html', author_list=authors, form=author_form)

@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除书籍出错')
            db.session.rollback()
    else:
        flash('书籍找不到')
    # redirect: 重定向,需要传入网络/路由地址
    return redirect(url_for("index"))

@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    author = Author.query.get(author_id)
    if author:
        try:
            # first delete the book
            Book.query.filter_by(author=author.id).delete()
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除作者出错')
            db.session.rollback()
    else:
        flash('作者找不到')
    # redirect: 重定向,需要传入网络/路由地址
    return redirect(url_for("index"))

if __name__ == '__main__':
    print("--")
    app.run(debug=True)
