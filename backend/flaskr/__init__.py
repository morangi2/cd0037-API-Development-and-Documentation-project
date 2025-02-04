from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(db_URI="", test_config=None):
    # create and configure the app
    app = Flask(__name__)
    if db_URI:
        setup_db(app, db_URI)
    else:
        setup_db(app)
        
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs == DONE
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS"
        )
        return response
    
    # test connection and local setup
    @app.route("/hello")
    def hello():
        return "Hello Mercy"

    """
    @TODO: == DONE
    Create an endpoint to handle GET requests for all available categories.

    Personal Notes
    - Controller is FormView.js, class is FormView(), componentDidMount()
    """
    @app.route("/categories")
    def retrieve_categories():
        try:
            selection = Category.query.order_by(Category.id).all()
            categories = {}

            for one_category in selection:
                categories[one_category.id] = one_category.type

            return jsonify(
                {
                    "success": True,
                    "categories": categories,
                    "total_categories": len(selection)
                }
            )
        except Exception as e:
            print(e)
            abort(404)

    """
    @TODO: == DONE
    Create an endpoint to handle GET requests for questions, including pagination (every 10 questions).
    This endpoint should return a list of questions, number of total questions, current category, categories.

    TEST: At this point, when you start the application you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.

    Personal Notes
    - Controller is QuestionView.js, method getQuestions()
    """

    @app.route("/questions")
    def retrieve_questions(category = "all"):
        try:
            selection_questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection_questions)

            if len(current_questions) == 0:
                abort(404)

            return jsonify(
                {
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                    "categories": retrieve_categories().json["categories"],
                    "current_category": category
                }
            )
        except:
            abort(404)


    """
    @TODO: == DONE
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.

    Personal Notes
    - Controller is QuestionView.js, method questionAction()
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            selected_question = Question.query.filter(Question.id == question_id).one_or_none()
            
            if selected_question is None:
                #no question with given ID
                abort(422)
            else:
                #delete the question then fetch the page afresh from the DB
                selected_question.delete()
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted_question": question_id,
                    "current_questions": current_questions,
                    "total_questions": len(selection)
                }
            )
        except:
            abort(422)

        
    """
    @TODO: == DONE
    Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.

    Personal Notes
    - Controller is FormView.js, method submitQuestion()
    - Code Review Notes: consider implementing a seperate route for search; /questions/search or /search == seperation of concers == good design principles
    """
    @app.route("/questions", methods=["POST"])
    def add_new_question():
        #retrieve the data submitted on post
        new_question_body = request.get_json()

        if new_question_body is None:
            abort(405)
        else:
            question = new_question_body.get("question", None)
            answer = new_question_body.get("answer", None)
            difficulty = new_question_body.get("difficulty", None)
            category = new_question_body.get("category", None)
            search = new_question_body.get("searchTerm", None)

            if search:
                # user submitted a search term
                #search for search term
                formatted_search_term = "%{}%".format(search)
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike(formatted_search_term))
                category = "all"
                #paginate the results
                current_questions = paginate_questions(request, selection)

                #return a jsonify
                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(selection.all()),
                        "current_category": category
                    }
                )

            else: 
                # user submitted a new question
                # - Code Review Notes:
                # -- Add in a check before inserting question in the DB so that the user is unable to insert empty entries as values for question or answer. 
                # -- In case the user tries inserting empty string values for question or answer, raise an appropriate exception.
                try:
                    #add to DB
                    question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
                    question.insert()

                    """ 
                    # paginate fresh fetch from DB and return page with list of questions
                    # no need to paginate as form resets for a new entry
                    selection = Question.query.order_by(Question.id).all()
                    current_questions = paginate_questions(request, selection) 
                    """

                    return jsonify(
                        {
                            "success": True,
                            "created_question_id": question.id,
                            "total_questions": len(Question.query.all())
                        }
                    )
                except:
                    abort(400)

    """
    @TODO: == DONE
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include only question that include that string within their question.
    Try using the word "title" to start.

    Personal Notes
    - Controller is QuestionView.js, method submitSearch()
    """
    # the TODO above has been implemented as part of the add_new_question() method


    """
    @TODO: == DONE
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the categories in the left column will cause only questions of that
    category to be shown.

    Personal Notes:
    - Controller; QuestionsView.js, method; getByCategory()
    """

    @app.route("/categories/<int:category_id>/questions")
    def questions_by_category(category_id):
        try:
            selection = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "current_category": category_id,
                    "total_questions":len(selection)
                }
            )
        except:
            abort(404) #resource not found, if URL is not correct


    """
    @TODO: == DONE -- this was the toughest end-point to implement logically
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category, one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.

    Personal Notes:
    - View; QuizView.js ... method; getNextQuestion()
    """

    @app.route("/quizzes", methods=["POST"])
    def get_quiz_questions():
        
        # set-the-stage) get the selected category details from the previous page
        body = request.get_json()  
        previous_questions = body.get("previous_questions", []) # returns a list
        quiz_category = body.get("quiz_category", None) # returns a dict eg==> {'type': 'Science', 'id': '1'}

        # 1) get the category_id selected
        if quiz_category:
            category_id = quiz_category.get("id")
        else:
            abort(400) # since game needs a category to be selected to continue

        # 2) get the questions, based on the category selected
        # PS: category_id = 0 == all categories, is not stored in the DB, hence if-else block below
        if category_id == 0: 
            questions = Question.query.all()
        else:
            questions = Question.query.filter(Question.category == category_id).all()

        # 3) get the total number of questions, based on category selected
        if len(questions) == 0:
            # no questions to play
            abort(400)
        else:
            total_questions = len(questions)

            # 4) compare total number of questions with list of prev questions
            # 4)a) if equal, end game
            if total_questions == len(previous_questions):
                return jsonify(
                    {
                        "success": True
                    }
                )

            # 4)b) if not equal, randomized game continues
            random_question_formatted = (random.choice(questions)).format()

            # CODE REVIEW NOTES
            # Check out notin_ method of the SQLAlchemy to filter out the questions which have already appeared in previous_questions list 
            # in a much more leaner and cleaner way by keeping track of the questions in the previous_questions
           
            # while the random question is in the list of previous questions, continue randomizing
            while random_question_formatted.get("id") in previous_questions: 
                random_question_formatted = (random.choice(questions)).format()

            return jsonify(
                {
                    "success": True,
                    "question": random_question_formatted,
                    "category": quiz_category
                }
            )


    """
    @TODO: == DONE
    Create error handlers for all expected errors including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            {
                "success": False,
                "error": 404,
                "message": "resource not found"
            }
        )
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify(
            {
                "error": 422,
                "message": "Unprocessable Entity",
                "success": False
            }
        )
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(
            {
                "error": 400,
                "message": "Bad Request",
                "success": False
            }
        )
    
    @app.errorhandler(405)
    def bad_request(error):
        return jsonify(
            {
                "error": 405,
                "message": "Method Not Allowed",
                "success": False
            }
        )

    return app
