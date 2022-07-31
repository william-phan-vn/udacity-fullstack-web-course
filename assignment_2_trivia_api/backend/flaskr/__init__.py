import json
import os
from http import HTTPStatus

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
from utils import paging


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after 
    completing the TODOs
    """
    CORS(app)
    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_all_categories():
        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories.update({str(category.id): category.type})
        return jsonify({
            'categories': formatted_categories
        })


    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_all_questions():
        page_key = request.args.get('page', 1, type=int)
        start, end = paging(page_key=page_key, page_size=10)

        questions = Question.query.all()
        paged_questions = questions[start:end]

        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories.update({category.id: category.type})

        return jsonify({
            'questions': [question.format() for question in paged_questions],
            'total_questions': len(questions),
            'categories': formatted_categories
        })

    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)
        question.delete()
        return jsonify(f'Question {question_id} deleted'), HTTPStatus.NO_CONTENT


    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        data = json.loads(request.data)
        try:
            question = Question(question=data.get('question'),
                                answer=data.get('answer'),
                                category=data.get('category'),
                                difficulty=data.get('difficulty'))
            question.insert()
            return jsonify(question.format()), HTTPStatus.CREATED
        except Exception as ex:
            print(ex)
            abort(HTTPStatus.UNPROCESSABLE_ENTITY)


    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        search_term = request.json.get('searchTerm')
        found_questions = Question.query.filter(
            Question.question.ilike('%' + search_term + '%')).all()
        return jsonify({
            'questions': [question.format() for question in found_questions],
            'total_questions': len(found_questions)
        })

    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<string:category_id>/questions')
    def get_category_questions(category_id):
        questions = Question.query.filter_by(category=category_id).all()
        if questions is None:
            abort(404)

        return jsonify({
            'questions': [question.format() for question in questions],
            'total_questions': len(questions)
        })

    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_next_questions():
        try:
            category = request.json.get('quiz_category').get('id')
            previous_questions = request.json.get('previous_questions')
        except:
            abort(HTTPStatus.BAD_REQUEST)
        questions = Question.query.filter_by(category=category).all()

        for question in questions:
            if question.id in previous_questions:
                continue
            else:
                return jsonify({'question': question.format()})

        return jsonify({'question': None})

    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource Not Found'
        }), 404

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Not Processable'
        }), 422

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500
    return app

