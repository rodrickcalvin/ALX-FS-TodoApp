import sys
from flask import Flask, abort, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# create instance of flask class / create flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abc@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo ID: {self.id}, description: {self.description}, complete: {self.complete}> '


class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

    def __repr__(self):
        return f'<TodoList ID: {self.id}, name: {self.name}, todos: {self.todos}>'


# create a todo item
@app.route('/todos/create', methods=['POST'])
def create_todo():
    body = {}
    error = False
    try:
        description = request.get_json()['description']
        list_id = request.get_json()['list_id']
        todo = Todo(description=description, completed=False, list_id=list_id)
        db.session.add(todo)
        db.session.commit()
        body['id'] = todo.id
        body['completed'] = todo.completed
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error == True:
        abort(500)
    else:
        return jsonify(body)



# update the completed status of a todo item
@app.route('/todos/<todo_id>/task-completed', methods=['POST'])
def update_todo(todo_id):
    error = False
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return redirect(url_for('index'))



# delete a todo item
@app.route('/todos/<todo_id>/delete', methods=['DELETE'])
def delete_todo(todo_id):
    error = False
    try:
        #Todo.query.filter_by(id=todo_id).delete()
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})


# set all todo as complete
@app.route('/todos/<todo_id>/set-task-completed', methods=['POST'])
def set_completed_todo(todo_id):
    error = False
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return '', 200



# create index route
# read all todo items from the database
@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))


# Get the lists and their todos
@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    lists = TodoList.query.all()
    active_list = TodoList.query.get(list_id)
    todos = Todo.query.filter_by(list_id=list_id).order_by('id').all()
    
    return render_template('index.html', todos=todos, lists=lists, active_list=active_list)


# create a new list
@app.route('/lists/create', methods=['POST'])
def create_list():
    error = False
    body = {}
    try:
        name = request.get_json()['name']
        todolist = TodoList(name=name)
        db.session.add(todolist)
        db.session.commit()
        body['id'] = todolist.id
        body['name'] = todolist.name
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify(body)


# delete list
@app.route('/lists/<list_id>/delete', methods=['DELETE'])
def delete_list(list_id):
    error = False
    try:
        list = TodoList.query.get(list_id)
        for todo in list.todos:
            db.session.delete(todo)

        db.session.delete(list)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})


# list completed when all task inside list are completed
@app.route('/lists/<list_id>/set-list-completed', methods=['POST'])
def list_completed(list_id):
    error = False
    try:
        list = TodoList.query.get(list_id)
        for todo in list.todos:
            todo.completed = True
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return '', 200


# FLASK-SETUP This code should be at the bottom of all your files.
if __name__ == '__main__':
    app.run(debug = True)
