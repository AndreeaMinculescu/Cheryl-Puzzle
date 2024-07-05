import customtkinter as ctk
from window import Window
from utilities import test_age_validity, test_email_validity, test_participant_no_validity
from CTkMessagebox import CTkMessagebox
from PIL import Image
import pandas as pd
import num2words


class PracticeApp:
    def __init__(self, master):
        """
        Class that manages the order of pages of the practice trials
        :param master: the window
        """
        self.master = master
        self.participant_no = None

        # order of form pages
        self.pages = [Page0(master, self), Page1(master, self), Page2(master, self), Page3(master, self),
                      Page4(master, self), Page5(master, self)]
        # current form page to be displayed
        self.current_page = 0
        # function to display the current form page
        self.show_current_page()

        # keep track of number of wrong answers (1 is allowed, 2 end the experiment)
        self.no_wrong_answers = 0

    def show_current_page(self):
        """
        Function to display the current page form in a grid format
        """
        self.pages[self.current_page].frame.grid(row=0, column=0, sticky="nsew")

    def show_next_page(self, idx):
        """
        Display the next form page given the order defined in the init function
        :param idx: the page to be displayed
        """
        self.pages[self.current_page].frame.grid_forget()
        self.current_page = idx
        # make sure that the "next" page exists
        if self.current_page < len(self.pages):
            self.show_current_page()
        else:
            self.master.quit()

    def show_previous_page(self):
        """
        Display the previous form page given the order defined in the init function
        """
        self.pages[self.current_page].frame.grid_forget()
        self.current_page -= 1
        # make sure that the "previous" page exists
        if self.current_page >= 0:
            self.show_current_page()

    @staticmethod
    def show_warning(title):
        """
        Define standard format of warnings
        :param title: title of warning
        """
        msg = CTkMessagebox(title="Warning", message=title, icon="img/warning.png")
        # if the message is not closed manually, it disappears after 10 seconds
        msg.after(10_000, msg.destroy)


class Page0:
    def __init__(self, master, app):
        """
        Third page is displayed when a comprehension question is answered incorrectly; then, the window is destroyed
        and the experiment ended
        :param master: the window object
        :param app: the form object
        """
        self.master = master
        self.app = app
        # each page is defined as a frame
        self.frame = ctk.CTkFrame(master, fg_color="#242424")

        # Define font size
        large_font = ('Arial', 18)

        # empty label such that text is placed in the middle of the screen
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=self.master.width / 15)
        l0.grid(column=0, row=0)

        # text to be displayed when a comprehension question is answered incorrectly
        self.text = "Please enter participant number:"
        # text label to display message + entry to type answer
        self.text_widget = ctk.CTkLabel(self.frame, text=self.text, font=large_font, height=self.master.height / 2,
                                        width=self.master.width / 1.2, text_color="#FFCC70")
        self.text_widget.grid(row=1, column=0, columnspan=2, pady=20, padx=self.master.width / 12, sticky="nsew")

        self.text_entry = ctk.CTkEntry(self.frame, font=large_font, text_color="#FFCC70", bg_color="#5A5A5A")
        self.text_entry.grid(row=2, column=0, pady=20, sticky="e")

        #####################################################
        # ok button to destroy the window and kill the program
        self.button = ctk.CTkButton(self.frame, text="OK", command=self.ok_button, font=large_font,
                                    fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.button.grid(row=3, column=0, pady=20, sticky="e")

    def ok_button(self):
        """
        Ok button logic: get participant number and move on to the next page
        """
        text_entry = self.text_entry.get()
        if text_entry == "":
            self.app.show_warning("Please fill in the participant number before continuing!")
            return
        elif not test_participant_no_validity(text_entry):
            self.app.show_warning("Please fill in a valid participant number!")
            return
        else:
            self.app.participant_no = int(text_entry)

        self.app.show_next_page(1)


class Page1:
    def __init__(self, master, app):
        """
        First page of the form displays general instructions
        :param master: the window object
        :param app: the practice trial object
        """
        self.master = master
        self.app = app
        # each page is defined as a frame
        self.frame = ctk.CTkFrame(master, fg_color="#242424")

        # Define font size
        large_font = ('Arial', 18)

        # for convenience, the instruction text is read from a txt file
        f = open(f"text/practice_intro.txt", "r")
        self.texts = f.read().split(";")
        f.close()

        ################################################
        # index to show one paragraph at a time
        self.current_text_index = 0

        # text label for instruction text
        self.text_widget = ctk.CTkTextbox(self.frame, font=large_font, height=self.master.height / 1.5,
                                          width=self.master.width / 1.2, state="disabled", text_color="#FFCC70",
                                          wrap=ctk.WORD)
        self.text_widget.configure(spacing2=10)
        self.text_widget.grid(row=0, column=0, columnspan=2, pady=20, padx=self.master.width / 12, sticky="nsew")
        # show first paragraph
        self.show_next_text()

        #####################################################
        # next button: when clicked it shows the next paragraph
        self.next_button = ctk.CTkButton(self.frame, text="Next", command=self.show_next_text, font=large_font,
                                         fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.next_button.grid(row=1, column=0, pady=20, sticky="e")

    def show_next_text(self):
        """
        Next button logic: if there is text to be displayed, show the next paragraph; otherwise, move on to the next
        page
        """
        if self.current_text_index < len(self.texts):
            self.text_widget.configure(state="normal")
            self.text_widget.insert(ctk.END, self.texts[self.current_text_index])
            self.text_widget.configure(state="disabled")
            self.current_text_index += 1

            # change button text for the last text
            if self.current_text_index == len(self.texts):
                self.next_button.configure(text="Go to next page")
        else:
            self.app.show_next_page(2)


class Page2:
    def __init__(self, master, app):
        """
        Second page of the practice form displays puzzle instructions
        :param master: the window object
        :param app: the form object
        """
        self.master = master
        self.app = app
        # each page is defined as a frame
        self.frame = ctk.CTkFrame(master, fg_color="#242424")

        # Define font size
        large_font = ('Arial', 18)

        # empty label such that text is placed in the middle of the screen
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=self.master.width / 6)
        l0.grid(column=0, row=0)

        # for convenience, the instruction puzzle text is read from a txt file
        f = open(f"text/practice_puzzle.txt", "r")
        self.texts = f.read().split(";")
        f.close()

        ##############################################
        # index to show one paragraph at a time
        self.current_text_index = 0
        # index to show one question at a time
        self.current_question_no = 0

        # comprehension questions, answer options and the correct answer
        self.question_text = ["Does Albert know that Cheryl only speaks the truth?", "Can Bernard make false claims?",
                              "What does Albert know about Cheryl's birthday right before his dialogue with Bernard?",
                              "Can Cheryl's birthday be on the 15th of May?",
                              "Who knows the birthday after the whispering and before the dialogue between Albert "
                              "and Bernard? \n(Note: multiple options may be true)", "Who knows the birthday after "
                              "the dialogue between Albert and Bernard? \n(Note: multiple options may be true)"]
        self.all_answer_options = [["Yes", "No", "Not specified"],
                                   ["Yes, he can make reasoning mistakes", "Yes, he may try to deceive Albert",
                                    "Yes, he may try to deceive Albert AND can make reasoning mistakes",
                                    "No, he only ever speaks the truth", "Not specified"],
                                   ["The day of Cheryl's birthday", "The month of Cheryl's birthday", "Both",
                                    "Not specified"], ["Yes", "No", "Not specified"],
                                   ["Albert", "Bernard", "Cheryl", "Neither", "Not specified"],
                                   ["Albert", "Bernard", "Cheryl", "Neither", "Not specified"]]
        self.correct_answers = [["Yes"], ["No, he only ever speaks the truth"], ["The month of Cheryl's birthday"],
                                ["No"], ["Cheryl"], ["Cheryl"]]

        # text label to display text
        self.text_widget = ctk.CTkTextbox(self.frame, font=large_font, height=self.master.height / 2.1,
                                          width=self.master.width / 1.2, state="disabled", text_color="#FFCC70",
                                          wrap=ctk.WORD, scrollbar_button_color="#4158D0",
                                          scrollbar_button_hover_color="#C850C0")
        self.text_widget.grid(row=0, column=0, columnspan=2, pady=20, padx=self.master.width / 12, sticky="nsew")
        self.show_next_text()

        ##################################################
        # next button: when clicked it shows the next paragraph/comprehension question
        self.next_button = ctk.CTkButton(self.frame, text="Next", command=self.show_next_text, font=large_font,
                                         fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.next_button.grid(row=20, column=0, pady=20, sticky="e")

    def show_next_text(self):
        """
        Next button logic: if there is text to be displayed, show the next paragraph; otherwise, display one
        comprehension question at a time; otherwise move on to the next page
        """
        # if possible, show the next paragraph of the puzzle instruction text
        if self.current_text_index < len(self.texts):
            self.text_widget.configure(state="normal")
            self.text_widget.insert(ctk.END, self.texts[self.current_text_index])
            self.text_widget.configure(state="disabled")
            self.current_text_index += 1
        # if there are no more questions to display, move on the last page
        elif self.current_question_no >= len(self.question_text):
            self.app.show_next_page(5)
        # if there are questions to display...
        else:
            # if this is not the first question...
            try:
                # check if answer to the previous question is correct
                flag_answer = self.check_answer(self.current_question_no-1)
                # if empty entry, then show warning and wait
                if flag_answer == -1:
                    return
                # delete previous question widgets
                self.label_question.grid_forget()
                for option in self.option_objects:
                    option.grid_forget()
            # if this is the first question then ignore
            except AttributeError:
                pass
            # show current question
            func = f"self.show_question({self.current_question_no})"
            exec(func)
            # increase question counter
            self.current_question_no += 1


    def show_question(self, idx):
        """
        Display question text and answer options
        :param idx: current question index
        """
        # define font size
        font = ('Arial', 16)

        # text label to display question
        self.label_question = ctk.CTkLabel(self.frame, text=self.question_text[idx], font=font)
        self.label_question.grid(row=1, column=0, padx=140, pady=10, sticky="w")

        # get answer options for current answers
        answer_options = self.all_answer_options[idx]
        row_counter = 1
        self.option_objects = []
        self.option_var_objects = []
        # display answer options and store objects for future deletion
        for option in answer_options:
            row_counter += 1
            options_var = ctk.IntVar()
            current_option = ctk.CTkCheckBox(self.frame, text=option, variable=options_var, font=font,
                                             fg_color="#4158D0", hover_color="#C850C0")
            self.option_var_objects.append(options_var)
            self.option_objects.append(current_option)
            current_option.grid(row=row_counter, column=1, padx=10, pady=5, sticky="w")

    def format_answer(self, idx_question):
        """
        Format answers from check-boxes: store answers selected into an array
        :param idx_question: index of the current question
        """
        answer_selected = []
        # check for each check-box if it has been selected
        for (idx, var) in enumerate(self.option_var_objects):
            is_selected = var.get()
            # if check-box was selected, then add corresponding answer to an array
            if is_selected:
                answer_selected.append(self.all_answer_options[idx_question][idx])
        print(self.question_text[idx_question])
        print(answer_selected)
        print("###########")
        return answer_selected

    def check_answer(self, idx_question):
        """
        Check if the answer to the current question is correct
        :param idx_question: index of the current question
        """
        # format answer to match the format of self.correct answers
        answer_selected = self.format_answer(idx_question)
        # if no answer provided, show warning and wait
        if not answer_selected:
            self.app.show_warning("Please fill in all entries before continuing")
            return -1

        # get correct answer
        correct_answers = self.correct_answers[idx_question]
        # if the number of selected answers is different from the number of correct answers, then it is incorrect,
        # so move to the third page
        if len(answer_selected) != len(correct_answers):
            self.app.no_wrong_answers += 1
            if self.app.no_wrong_answers == 1:
                # try the same question again
                self.current_question_no -= 1
                self.app.show_next_page(4)
                return
            else:
                self.app.show_next_page(3)

        # if any of the selected answers is incorrect, then more to the third page
        for i in range(len(answer_selected)):
            if correct_answers[i] != answer_selected[i]:
                self.app.no_wrong_answers += 1
                if self.app.no_wrong_answers == 1:
                    # try the same question again
                    self.current_question_no -= 1
                    self.app.show_next_page(4)
                else:
                    self.app.show_next_page(3)
        return 1


class Page3:
    def __init__(self, master, app):
        """
        Third page is displayed when a comprehension question is answered incorrectly; then, the window is destroyed
        and the experiment ended
        :param master: the window object
        :param app: the form object
        """
        self.master = master
        self.app = app
        # each page is defined as a frame
        self.frame = ctk.CTkFrame(master, fg_color="#242424")

        # Define font size
        large_font = ('Arial', 18)

        # empty label such that text is placed in the middle of the screen
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=self.master.width / 15)
        l0.grid(column=0, row=0)

        # text to be displayed when a comprehension question is answered incorrectly
        self.text = "Wrong answer. The experiment will end now. \nPlease alert the experimenter if you think this is " \
                    "not correct."
        # text label to display message
        self.text_widget = ctk.CTkLabel(self.frame, text=self.text, font=large_font, height=self.master.height / 2,
                                        width=self.master.width / 1.2, text_color="#FFCC70")
        self.text_widget.grid(row=1, column=0, columnspan=2, pady=20, padx=self.master.width / 12, sticky="nsew")

        #####################################################
        # ok button to destroy the window and kill the program
        self.button = ctk.CTkButton(self.frame, text="OK", command=self.ok_button, font=large_font,
                                    fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.button.grid(row=2, column=0, pady=20, sticky="e")

    def ok_button(self):
        """
        Ok button logic: destroy the window and kill the program
        """
        self.master.destroy()
        exit()


class Page4:
    def __init__(self, master, app):
        """
        Third page is displayed when a comprehension question is answered incorrectly; then, the window is destroyed
        and the experiment ended
        :param master: the window object
        :param app: the form object
        """
        self.master = master
        self.app = app
        # each page is defined as a frame
        self.frame = ctk.CTkFrame(master, fg_color="#242424")

        # Define font size
        large_font = ('Arial', 18)

        # empty label such that text is placed in the middle of the screen
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=self.master.width / 15)
        l0.grid(column=0, row=0)

        # text to be displayed when a comprehension question is answered incorrectly
        self.text = "Wrong answer. Please read the instruction text one more time and try again. \nWARNING: At the " \
                    "next incorrect answer, the experiment will automatically end!"
        # text label to display message
        self.text_widget = ctk.CTkLabel(self.frame, text=self.text, font=large_font, height=self.master.height / 2,
                                        width=self.master.width / 1.2, text_color="#FFCC70")
        self.text_widget.grid(row=1, column=0, columnspan=2, pady=20, padx=self.master.width / 12, sticky="nsew")

        #####################################################
        # ok button to destroy the window and kill the program
        self.button = ctk.CTkButton(self.frame, text="OK", command=self.ok_button, font=large_font,
                                    fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.button.grid(row=2, column=0, pady=20, sticky="e")

    def ok_button(self):
        """
        Ok button logic: destroy the window and kill the program
        """
        self.app.show_next_page(2)


class Page5:
    def __init__(self, master, app):
        """
        Fourth page of the practice trials is displayed when all comprehension questions have been answered correctly
        :param master: the window object
        :param app: the form object
        """
        self.master = master
        self.app = app
        # each page is defined as a frame
        self.frame = ctk.CTkFrame(master, fg_color="#242424")

        # Define font size
        large_font = ('Arial', 18)

        # empty label such that text is placed in the middle of the screen
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=self.master.width / 15)
        l0.grid(column=0, row=0)

        # for convenience, the outro text is read from a txt file
        f = open(f"text/practice_outro.txt", "r")
        self.text = f.read()
        f.close()

        ########################################################
        # text label to display outro text
        self.text_widget = ctk.CTkLabel(self.frame, text=self.text, font=large_font, height=self.master.height / 2,
                                        width=self.master.width / 1.2, text_color="#FFCC70")
        self.text_widget.grid(row=1, column=0, columnspan=2, pady=20, padx=self.master.width / 12, sticky="nsew")

        ###########################################################
        # start button to proceed to the puzzle
        self.button = ctk.CTkButton(self.frame, text="Start", command=self.ok_button, font=large_font,
                                    fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.button.grid(row=2, column=0, pady=20, sticky="e")

    def ok_button(self):
        """
        Ok button logic: destroy text label and ok button, quit current window
        """
        self.button.destroy()
        self.text_widget.destroy()
        self.master.quit()


if __name__ == "__main__":
    # for testing purposes; normally called from quickstart.py
    root = Window("Practice Trials")
    app = PracticeApp(root)
    root.mainloop()
