import connection
from psycopg2.extensions import AsIs
from datetime import datetime


@connection.connection_handler
def get_questions(cursor):
    cursor.execute("""SELECT * FROM question ORDER BY submission_time DESC LIMIT 5;""")
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def delete_question(cursor, question_id):
    cursor.execute("""DELETE FROM question_tag WHERE question_id=%(question_id)s;""", {'question_id': question_id})
    cursor.execute("""DELETE FROM comment WHERE question_id=%(question_id)s;""", {'question_id': question_id})
    cursor.execute("""DELETE FROM answer WHERE question_id=%(question_id)s;""", {'question_id': question_id})
    cursor.execute("""DELETE FROM question WHERE id=%(id)s;""", {'id': question_id})


@connection.connection_handler
def get_latest5_questions(cursor,order,direction):
    cursor.execute("""SELECT * FROM question ORDER BY %(order)s %(direction)s;""", {"order": AsIs(order), "direction":AsIs(direction.upper())})
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def get_answers(cursor):
    cursor.execute("""SELECT * FROM answer ORDER BY submission_time DESC;""")
    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def delete_answer(cursor, answer_id):
    cursor.execute("""DELETE FROM comment WHERE answer_id=%(answer_id)s;""", {'answer_id': answer_id})
    cursor.execute("""DELETE FROM answer WHERE id=%(answer_id)s;""", {'answer_id': answer_id})


@connection.connection_handler
def get_comments(cursor):
    cursor.execute("""SELECT * FROM comment ORDER BY submission_time DESC;""")
    comments = cursor.fetchall()
    return comments


@connection.connection_handler
def add_question(cursor, title, message):
    user_story = {
        'submission_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'view_number': 0,
        'vote_number': 0,
        'title': title,
        'message': message,
        'image': ""
    }

    cursor.execute("""INSERT INTO question(submission_time, view_number, vote_number, title, message, image)
                      VALUES(%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s);""",
                   user_story)

    cursor.execute("""SELECT id FROM question
                      ORDER BY id DESC
                      LIMIT 1;""")
    return cursor.fetchone()['id']


@connection.connection_handler
def add_answer(cursor, question_id, message):

    user_story = {
        'submission_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'vote_number': 0,
        'question_id': question_id,
        'message': message,
        'image': ""
    }

    cursor.execute("""INSERT INTO answer(submission_time, vote_number, question_id, message, image)
                      VALUES(%(submission_time)s,%(vote_number)s,%(question_id)s, %(message)s,%(image)s);""", user_story)


@connection.connection_handler
def add_comment(cursor, question_id, answer_id, message):
    if question_id == '':
        user_story = {
            'submission_time': datetime.now(),
            'message': message,
            'answer_id': answer_id
        }

        cursor.execute("""INSERT INTO comment(submission_time, answer_id, message)
                          VALUES(%(submission_time)s, %(answer_id)s, %(message)s);""", user_story)

    elif answer_id == '':
        user_story = {
            'submission_time': datetime.now(),
            'message': message,
            'question_id': question_id
        }

        cursor.execute("""INSERT INTO comment(submission_time, question_id, message)
                                  VALUES(%(submission_time)s, %(question_id)s, %(message)s);""", user_story)


@connection.connection_handler
def delete_comments(cursor, comment_id):
    cursor.execute("""DELETE FROM comment WHERE id=%(comment_id)s;""", {'comment_id': comment_id})


@connection.connection_handler
def get_update(cursor,answer_id , message):
    time = datetime.now()
    cursor.execute("""UPDATE answer SET message = %(message)s,submission_time = %(time)s WHERE id=%(answer_id)s;""",
                   {"message": message, 'answer_id': answer_id, 'time': time})


@connection.connection_handler
def get_update_for_comment(cursor, comment_id, message):
    time = datetime.now()
    cursor.execute("""UPDATE comment SET 
                      message = %(message)s, 
                      submission_time = %(time)s, 
                      edited_count = %(count)s 
                      WHERE id=%(comment_id)s;""", {"message": message, 'comment_id': comment_id, 'time': time, 'count': 1})


@connection.connection_handler
def get_new_update_for_comment(cursor, comment_id, message):
    time = datetime.now()
    cursor.execute("""UPDATE comment SET 
                      message = %(message)s, 
                      submission_time = %(time)s, 
                      edited_count = edited_count + 1 
                      WHERE id=%(comment_id)s;""", {"message": message, 'comment_id': comment_id, 'time': time})


@connection.connection_handler
def get_question_id(cursor, answer_id):
    cursor.execute("""
                    SELECT * FROM answer
                    WHERE id=%(id)s LIMIT 1
                   """,
                   {'id': answer_id})
    return cursor.fetchone()['question_id']


@connection.connection_handler
def get_question_id_for_comment(cursor, comment_id):
    cursor.execute("""
                    SELECT * FROM comment
                    WHERE id=%(id)s LIMIT 1
                   """,
                   {'id': comment_id})
    return cursor.fetchone()['question_id']


@connection.connection_handler
def search_in(cursor, searched_word):
    cursor.execute("""SELECT question.* FROM question LEFT JOIN answer ON question.id = answer.question_id
                      WHERE (LOWER(title) LIKE %(searched_word)s OR LOWER(answer.message) LIKE %(searched_word)s OR LOWER(question.message) LIKE %(searched_word)s);""",
                   {'searched_word': '%' + searched_word + '%'})
    searched_data = cursor.fetchall()
    return searched_data


@connection.connection_handler
def vote_up_question(cursor, question_id):

    variables = {
        'question_id': question_id
    }

    cursor.execute("""UPDATE question
                      SET vote_number = vote_number+1
                      WHERE id = %(question_id)s;""", variables)


@connection.connection_handler
def vote_down_question(cursor, question_id):

    variables = {
        'question_id': question_id
    }

    cursor.execute("""UPDATE question
                      SET vote_number = vote_number-1
                      WHERE id = %(question_id)s;""", variables)


@connection.connection_handler
def vote_up_answer(cursor, question_id, answer_id):

    variables = {
        'question_id': question_id,
        'answer_id': answer_id
    }

    cursor.execute("""UPDATE answer
                      SET vote_number = vote_number+1
                      WHERE question_id = %(question_id)s AND id = %(answer_id)s;""", variables)


@connection.connection_handler
def vote_down_answer(cursor, question_id, answer_id):

    variables = {
        'question_id': question_id,
        'answer_id': answer_id
    }

    cursor.execute("""UPDATE answer
                      SET vote_number = vote_number-1
                      WHERE question_id = %(question_id)s AND id = %(answer_id)s;""", variables)
