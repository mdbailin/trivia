import json
import os
from flask import Flask, flash, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  DONE
  '''

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  DONE
  '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        if len(categories) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'categories': {category.id: category.type for category in categories},
                'all_categories': len(categories)
            })

    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  DONE
  '''
    @app.route('/questions', methods=['GET'])
    def get_question():
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + 10
      questions = Question.query.order_by(Question.id).all()
      formatted_questions = [question.format() for question in questions]
      categories = Category.query.order_by(Category.id).all()
      
      if len(formatted_questions[start:end]) == 0:
        abort(404)
      else:
        return jsonify({
          'success': True,
          'total_questions': len(questions),
          'questions': formatted_questions[start:end],
          'categories': {cat.id: cat.type for cat in categories},
          'current_category': None
        }) 

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  DONE 
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
      try:
        question = Question.query.filter(Question.id == question_id).one_or_none()
        if question is None:
          abort(404)
        
        question.delete()

        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + 10
        questions = Question.query.order_by(Question.id).all()
        formatted_questions = [question.format() for question in questions]

        return jsonify({
          'success': True,
          'deleted': question_id,
          'questions': formatted_questions[start:end],
          'total_questions': len(questions)
        })
      except:
        abort(422)

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  DONE  
  '''
    @app.route('/questions', methods=['POST'])
  # curl -X POST \
  # -H "Content-Type: application/json" \
  # -d '{"question":"How many continents on earth?", "answer":"Seven", "category":"3","difficulty":"1"}' \
  # http://127.0.0.1:5000/questions 
    def create_question():
      body = request.get_json()

      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_difficulty = body.get('difficulty', None)
      new_category = body.get('category', None)
      searchTerm = body.get('searchTerm', None)
      try:

        if searchTerm:
          questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(searchTerm)))
          page = request.args.get('page', 1, type=int)
          start = (page - 1) * QUESTIONS_PER_PAGE
          end = start + 10
          searched_questions = [question.format() for question in questions]

          return jsonify({
            'success': True,
            'searchTerm': searchTerm,
            'questions': searched_questions[start:end],
            'total_questions': len(searched_questions)
          })
        else:
          question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
          question.insert()
          
          page = request.args.get('page', 1, type=int)
          start = (page - 1) * QUESTIONS_PER_PAGE
          end = start + 10
          questions = Question.query.order_by(Question.id).all()
          formatted_questions = [question.format() for question in questions]

          return jsonify({
            'success': True,
            'question_id': question.id,
            'questions': formatted_questions[start:end],
            'total_questions': len(Question.query.all()),
            'current_category': new_category
          })
      except:
        abort(422)
    

      

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  DONE
  '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])

    # matthewbailin@matthewbailin trivia % curl -X POST \
    # -H "Content-Type: application/json" \
    # -d '{"search": "Tom"}' \
    # http://127.0.0.1:5000/questions | jq '.'
    def get_questions_by_category(category_id):
      questions = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
      if len(questions) == 0:
          return abort(404)
      try:
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + 10
        formatted_questions = [question.format() for question in questions]
        current_category = Category.query.get(category_id).type

        return jsonify({
              'success': True,
              'questions': formatted_questions[start:end],
              'total_questions': len(questions),
              'current_category': current_category
            })
      except:
        abort(422)

  


      '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    @app.route('/quizzes', methods=['POST'])
    # curl -X POST "http://127.0.0.1:5000/quizzes" -d 
    # "{\"quiz_category\":{\"type\": \"History\", \"id\": \"4\"},\"previous_questions\":[2]}" 
    # -H "Content-Type: application/json"
    def play_quiz():
      body = request.get_json()
      previous_questions = body.get('previous_questions', [])
      quiz_category = body.get('quiz_category', None)

      try:
        if quiz_category:
          if quiz_category['id'] == 0:
            quiz = Question.query.all()
          else:
            quiz = Question.query.filter(Question.category == quiz_category['id']).all()
          if not quiz:
            abort(422)
          selected = []
          for question in quiz:
            if question.id not in previous_questions:
              selected.append(question.format())
          if len(selected) != 0:
            result = random.choice(selected)
            return jsonify({
              'success': True,
              'question': result
            })
          else:
            return jsonify ({
              'question': False
            })
      except:
        abort(422)
    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  DONE 
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
            }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422
    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  DONE
  '''

    return app
