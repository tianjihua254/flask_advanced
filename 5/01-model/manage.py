import os
from flask import Flask
from flask_script import Manager, prompt_bool, Shell
# 导入类库
from flask_sqlalchemy import SQLAlchemy
# 导入数据库迁移类库
from flask_migrate import Migrate, MigrateCommand
app = Flask(__name__)
# 配置数据库连接地址
base_dir = os.path.abspath(os.path.dirname(__name__))
database_uri = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
# 禁止对象的修改追踪
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 配置自动提交(在请求结束时自动执行提交操作)，
# 否则每次数据库操作后都需要手动提交db.session.commit()
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# 创建对象
db = SQLAlchemy(app)


# 定义模型，必须继承自db.Model
class User(db.Model):
    # 可以指定表名，若不指定会默认将模型类名的'小写+下划线'
    # 如：模型名为UserModel，则默认表名为user_model
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(32))


# 创建数据库表，测试时需要注意以下方面
# 连接sqlite：数据库不用创建，不存在会自动创建
# 连接MySQL：数据库需要提前创建好，否则连接失败
@app.route('/create/')
def create():
    # 表如果已经存在，则不会覆盖创建
    # 表更新时可以粗暴的先删除在创建
    db.drop_all()
    db.create_all()
    return '数据表创建成功'

# 删除数据表
@app.route('/drop/')
def drop():
    db.drop_all()
    return '数据表删除成功'


@app.route('/')
def index():
    return '数据模型'


# 增加数据
@app.route('/insert/')
def insert():
    # 创建一个模型对象
    #liang = User(username='liang', email='liang@163.com')
    #yanxu = User(username='yanxu', email='yanxu@163.com')
    # 增加一条数据
    #db.session.add(yanxu)

    bing = User(username='bing', email='bing@163.com')
    mei = User(username='mei', email='mei@163.com')
    yu = User(username='yu', email='yu@163.com')
    xiang = User(username='xiang', email='xiang@163.com')
    xuer = User(username='xuer', email='xuer@163.com')
    # 增加多条数据
    db.session.add_all([bing, mei, yu, xiang, xuer])
    # 提交操作，所有的数据库操作都必须提交后才有效
    #db.session.commit()
    return '数据添加成功'


# 查询数据
@app.route('/select/<int:uid>')
def select(uid):
    # 根据id查询数据
    user = User.query.get(uid)
    if user:
        return user.username
    else:
        return '不存在此ID'


# 修改数据
@app.route('/update/<int:uid>')
def update(uid):
    user = User.query.get(uid)
    if user:
        user.email = 'xxx@163.com'
        # 没有单独的更新数据的函数
        db.session.add(user)
        return '数据修改成功'
    else:
        return '不存在此ID'


# 删除数据(通过情况下不做物理删除)
@app.route('/delete/<int:uid>')
def delete(uid):
    user = User.query.get(uid)
    if user:
        db.session.delete(user)
        return '数据删除成功'
    else:
        return '不存在此ID'


# 条件查询
@app.route('/selectby/')
def select_by():
    # 根据ID查询
    #user = User.query.get(1)
    #return user.username

    # 查询所有数据
    #users = User.query.all()
    #return str(users)

    # 查询第一条数据
    #user = User.query.first()
    #return user.username

    # 指定等值条件，可以写多个条件
    #user = User.query.filter_by(id=3).first()
    #user = User.query.filter_by(email='mei@163.com').first()
    #return user.username

    # 指定特定条件
    #user = User.query.filter(User.id > 3).first()
    #return user.username

    # 找到就返回，没有就报404错误
    #user = User.query.get_or_404(8)
    #user = User.query.filter(User.id > 8).first_or_404()
    #return user.username

    # 统计总数
    count = User.query.filter(User.id > 3).count()
    return 'id > 3的数据共有%d条' % count


manager = Manager(app)
migrate = Migrate(app, db)
# 添加终端命令
manager.add_command('db', MigrateCommand)


# 定制shell
def shell_make_context():
    # 返回的数据作为shell启动时的上下文
    return dict(db=db, User=User)
manager.add_command('shell', Shell(make_context=shell_make_context))


# 添加终端创建数据表命令
@manager.command
def createall():
    db.create_all()
    return '数据表已创建'


# 添加终端删除数据表命令
@manager.command
def dropall():
    # 终端下给与简单的确认提示
    if prompt_bool('确定要删除所有数据表吗?'):
        db.drop_all()
        return '数据表已删除'
    else:
        return '最好再考虑一下'

# 蓝本创建后不能使用，需要注册才可以
from user import user
# 注册蓝本，可以顺便指定蓝本中的路由前缀
app.register_blueprint(user, url_prefix='/user')


if __name__ == '__main__':
    manager.run()
