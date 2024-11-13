from flask import make_response

class Menu:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.questions = {
            "Nutrition": [
                {"question": "Which vitamin is abundant in citrus fruits?", "options": ["Vitamin A", "Vitamin C", "Vitamin D"], "answer": "Vitamin C"},
                {"question": "What is the main source of protein?", "options": ["Fruits", "Vegetables", "Meat"], "answer": "Meat"},
                {"question": "Which mineral is essential for healthy bones?", "options": ["Iron", "Calcium", "Potassium"], "answer": "Calcium"}
            ],
            "Gender Equality": [
                {"question": "Which day is celebrated as International Women's Day?", "options": ["March 8", "April 7", "May 5"], "answer": "March 8"},
                {"question": "What is the aim of gender equality?", "options": ["Dominance", "Equity", "Supremacy"], "answer": "Equity"},
                {"question": "Which organization promotes gender equality?", "options": ["UNESCO", "UNICEF", "UN Women"], "answer": "UN Women"}
            ]
        }
        self.current_question = 0
        self.correct_answers = 0
        self.total_questions = 0
        self.selected_topic = ""
        self.feedback_storage = []

    def generate_ussd_response(self, response_text, end=False):
        response_prefix = "END" if end else "CON"
        response = f"{response_prefix} {response_text}"
        return make_response(response, 200)

    def home(self, session_id, text):
        """Main menu with options"""
        if text == '':
            menu_text = "Welcome to the Ubumwe app.\n"
            menu_text += "1. Articles\n"
            menu_text += "2. Play Quiz\n"
            menu_text += "3. Send Feedback\n"
            menu_text += "4. Admin"
            return self.generate_ussd_response(menu_text)
        
        elif text == '1':
            return self.articles_menu(session_id, '')
        
        elif text == '2':
            return self.play_games_menu(session_id, '')
        
        elif text == '3':
            return self.send_feedback_menu(session_id, '')
        
        elif text == '4':
            return self.admin_menu(session_id, '')
        
        else:
            return self.generate_ussd_response("Invalid option. Please try again.", end=True)

    def articles_menu(self, session_id, text):
        """Articles submenu"""
        if text == '':
            menu_text = "Choose an article category:\n"
            menu_text += "1. Child Protection\n"
            menu_text += "2. Equality\n"
            menu_text += "3. Nutrition"
            return self.generate_ussd_response(menu_text)
        
        elif text == '1':
            return self.generate_ussd_response("Child Protection article content...", end=True)
        
        elif text == '2':
            return self.generate_ussd_response("Equality article content...", end=True)
        
        elif text == '3':
            return self.generate_ussd_response("Nutrition article content...", end=True)
        
        else:
            return self.generate_ussd_response("Invalid selection. Please try again.", end=True)

    def play_games_menu(self, session_id, text):
        """Games submenu"""
        if text == '':
            menu_text = "Choose a quiz topic:\n"
            menu_text += "1. Nutrition\n"
            menu_text += "2. Gender Equality"
            return self.generate_ussd_response(menu_text)
        
        elif text == '1':
            # Set the topic to Nutrition and start the quiz
            self.selected_topic = "Nutrition"
            self.current_question = 0
            self.correct_answers = 0
            self.total_questions = len(self.questions[self.selected_topic])
            return self.ask_question(session_id)
        
        elif text == '2':
            # Set the topic to Gender Equality and start the quiz
            self.selected_topic = "Gender Equality"
            self.current_question = 0
            self.correct_answers = 0
            self.total_questions = len(self.questions[self.selected_topic])
            return self.ask_question(session_id)
        
        else:
            return self.generate_ussd_response("Invalid selection. Please try again.", end=True)

    def ask_question(self, session_id):
        """Ask the next question in the quiz"""
        question = self.questions[self.selected_topic][self.current_question]
        menu_text = f"Question {self.current_question + 1}: {question['question']}\n"
        menu_text += "\n".join([f"{i + 1}. {option}" for i, option in enumerate(question['options'])])
        menu_text += "\nChoose your answer (1, 2, 3)."
        return self.generate_ussd_response(menu_text)

    def check_answer(self, session_id, text):
        """Check if the chosen answer is correct"""
        question = self.questions[self.selected_topic][self.current_question]
        try:
            chosen_answer = question['options'][int(text) - 1]
        except IndexError:
            return self.generate_ussd_response("Invalid selection. Please try again.", end=True)
        
        if chosen_answer == question['answer']:
            self.correct_answers += 1
            response = "Correct! "
        else:
            response = "Incorrect! "
        
        self.current_question += 1

        if self.current_question < self.total_questions:
            response += "Next question...\n"
            return self.ask_question(session_id)
        else:
            return self.end_game(session_id)

    def end_game(self, session_id):
        """End the quiz and show a final message"""
        response = f"Thank you for playing! You've completed the quiz.\nYour score: {self.correct_answers}/{self.total_questions}"
        return self.generate_ussd_response(response, end=True)
