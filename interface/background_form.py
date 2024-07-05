import customtkinter as ctk
from window import Window
from utilities import test_age_validity, test_email_validity
from CTkMessagebox import CTkMessagebox
import pandas as pd


class FormApp:
    def __init__(self, master, puzzle_answers=[{}], subject_id="test", reward_sum=7.5, reward_idx=None):
        """
        Class that manages the order of pages of the form
        :param master: the window
        :param puzzle_answers: list of answers given to puzzle (to be merged with form answers)
        :param subject_id: unique subject id (to be saved with contact information)
        :param reward_sum: base reward sum for participating in the experiment
        :param reward_idx: index of the puzzle randomly selected to decide whether to apply monetary bonus
        """
        self.master = master
        self.dict_puzzle_answers = puzzle_answers
        self.subject_id = subject_id
        self.reward_sum = reward_sum
        self.reward_idx = reward_idx
        # arrays to store form answers
        self.dict_form_answers_private = {}
        self.dict_form_answers_public = {}

        # order of form pages
        self.pages = [Page0(master, self), Page1(master, self), Page2(master, self), Page3(master, self),
                      Page4(master, self), Page5(master, self)]
        # current form page to be displayed
        self.current_page = 0
        # function to display the current form page
        self.show_current_page()

    def show_current_page(self):
        """
        Function to display the current page form in a grid format
        """
        self.pages[self.current_page].frame.grid(row=0, column=0, sticky="nsew")

    def show_next_page(self):
        """
        Display the next form page given the order defined in the init function
        """
        self.pages[self.current_page].frame.grid_forget()
        self.current_page += 1
        # make sure that the "next" page exists
        if self.current_page < len(self.pages):
            self.show_current_page()

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
        First page of the form displays instructions
        :param master: the window object
        :param app: the form object
        """
        self.master = master
        self.app = app
        # each page is defined as a frame
        self.frame = ctk.CTkFrame(master, fg_color="#242424")

        # Define font size
        large_font = ('Arial', 16)

        # empty label such that text is placed in the middle of the screen
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=self.master.width / 6)
        l0.grid(column=0, row=0)

        # for convenience, the instruction text is read from a txt file
        f = open(f"text/background_form_intro.txt", "r")
        intro_text = f.read()
        f.close()

        ##################################################################
        # display text in a label
        self.label_title = ctk.CTkLabel(self.frame, text=intro_text, font=('Arial', 18), text_color="#FFCC70",
                                        width=self.master.width)
        self.label_title.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ###################################################################
        # submit button to go to the next page
        self.submit_button = ctk.CTkButton(self.frame, text="Start form", command=self.submit_form, font=large_font,
                                           fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.submit_button.grid(row=2, column=0, pady=10)

    def submit_form(self):
        """
        Submit button logic: go to the next page
        """
        self.label_title.destroy()
        self.submit_button.destroy()
        self.app.show_next_page()


class Page1:
    def __init__(self, master, app):
        """
        Second page of the form displays questions pertaining to demographic data
        :param master: the window object
        :param app: the form object
        """
        self.master = master
        self.app = app
        # each page is defined as a frame
        self.frame = ctk.CTkFrame(master, fg_color="#242424")

        # define font size
        large_font = ('Arial', 16)

        # display title of page in a label
        self.label_title = ctk.CTkLabel(self.frame, text="Demographic data", font=('Arial', 18), text_color="#FFCC70")
        self.label_title.grid(row=0, column=0, padx=10, pady=10)

        #################################################################
        # first question: "What is your name" + entry to type the answer
        self.label_name = ctk.CTkLabel(self.frame, text="What is your name?", font=large_font)
        self.label_name.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_name = ctk.CTkEntry(self.frame, font=large_font, width=self.master.width / 2,
                                       text_color="#FFCC70", bg_color="#5A5A5A")
        self.entry_name.grid(row=1, column=1, padx=10, pady=10)

        ##################################################################
        # empty space between questions
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=30)
        l0.grid(column=0, row=2)

        # second question: "What is your email address" + entry to type the answer
        self.label_email = ctk.CTkLabel(self.frame, text="What is your email address? (preferably same as the one "
                                                         "registered on RbpReg)", font=large_font)
        self.label_email.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.entry_email = ctk.CTkEntry(self.frame, font=large_font, width=self.master.width / 2,
                                        text_color="#FFCC70", bg_color="#5A5A5A")
        self.entry_email.grid(row=3, column=1, padx=10, pady=10)

        #####################################################################
        # empty space between questions
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=30)
        l0.grid(column=0, row=4)

        # third question: "What is your gender"
        self.label_gender = ctk.CTkLabel(self.frame, text="What is your gender?", font=large_font)
        self.label_gender.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        # multiple choices (only one can be selected at a time)
        self.gender_var = ctk.StringVar()
        gender_options = ["Male", "Female", "Other", "Prefer not to say"]
        row_counter = 5
        for option in gender_options:
            row_counter += 1
            ctk.CTkRadioButton(self.frame, text=option, variable=self.gender_var, value=option, font=large_font,
                               fg_color="#4158D0", hover_color="#C850C0") \
                .grid(row=row_counter, column=1, padx=10, pady=5, sticky="w")

        #########################################################################
        # empty space between questions
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=30)
        l0.grid(column=0, row=row_counter + 1)

        # fourth question: "What is your age?" + entry to type answers
        self.label_age = ctk.CTkLabel(self.frame, text="What is your age?", font=large_font)
        self.label_age.grid(row=row_counter + 2, column=0, padx=10, pady=10, sticky="w")
        self.entry_age = ctk.CTkEntry(self.frame, font=large_font, width=50,
                                      text_color="#FFCC70", bg_color="#5A5A5A")
        self.entry_age.grid(row=row_counter + 2, column=1, padx=10, pady=10, sticky="w")

        ###########################################################################
        # submit button to go to the next page
        self.submit_button = ctk.CTkButton(self.frame, text="Next", command=self.submit_form, font=large_font,
                                           fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.submit_button.grid(row=row_counter + 3, column=1, padx=10, pady=20, sticky="w")

    def submit_form(self):
        """
        Submit button logic: check that all entries have been filled in, check validity of answers and move to the
        next page
        """
        # store all answers
        name = self.entry_name.get()
        email = self.entry_email.get()
        gender = self.gender_var.get()
        age = self.entry_age.get()

        # if an entry is empty, show warning and wait
        if name == "" or email == "" or gender == "" or age == "":
            self.app.show_warning("Please fill in all entries before continuing")
        # if the age is not a valid number, show warning and wait
        elif not test_age_validity(age):
            self.app.show_warning("Please fill in a valid age")
        # if the email address is not valid, show warning and wait
        elif not test_email_validity(email):
            self.app.show_warning("Please fill in a valid email address")
        # else, store answers and move to the next page
        else:
            # store name and email separately from the rest of the answers
            self.app.dict_form_answers_private = {"Subject id": self.app.subject_id, "Name": name, "Email": email,
                                                  "Reward sum": self.app.reward_sum, "Reward idx": self.app.reward_idx}
            self.app.dict_form_answers_public = self.app.dict_form_answers_public | \
                                                {"Gender": gender, "Age": age}
            self.app.show_next_page()


class Page2:
    def __init__(self, master, app):
        """
        Third page of the form displays questions pertaining to study information
        :param master: the window object
        :param app: the form object
        """
        self.master = master
        self.app = app
        # each page is defined as a frame object
        self.frame = ctk.CTkFrame(master, fg_color="#242424")

        # define font size
        large_font = ('Arial', 16)

        # define title of page as label
        self.label_title = ctk.CTkLabel(self.frame, text="Study information", font=('Arial', 18), text_color="#FFCC70")
        self.label_title.grid(row=0, column=0, padx=10, pady=10)

        #########################################
        # first question: "Are you a RUG student?"
        self.label_rug = ctk.CTkLabel(self.frame, text="Are you a RUG student?", font=large_font)
        self.label_rug.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # two option: Yes/No
        self.rug_var = ctk.StringVar()
        rug_options = ["Yes", "No"]
        row_counter = 2
        for option in rug_options:
            row_counter += 1
            ctk.CTkRadioButton(self.frame, text=option, variable=self.rug_var, value=option, font=large_font,
                               fg_color="#4158D0", hover_color="#C850C0") \
                .grid(row=row_counter, column=1, padx=10, pady=5, sticky="w")

        #######################################################
        # empty space between questions
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=30)
        l0.grid(column=0, row=5)

        # second question: "Are you a Bachelor student?"
        self.label_bsc = ctk.CTkLabel(self.frame, text="Are you a Bachelor student?", font=large_font)
        self.label_bsc.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        # two options: Yes/No
        self.bsc_var = ctk.StringVar()
        bsc_options = ["Yes", "No"]
        row_counter = 6
        for option in bsc_options:
            row_counter += 1
            ctk.CTkRadioButton(self.frame, text=option, variable=self.bsc_var, value=option, font=large_font,
                               fg_color="#4158D0", hover_color="#C850C0") \
                .grid(row=row_counter, column=1, padx=10, pady=5, sticky="w")

        ############################################################
        # empty space between questions
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=30)
        l0.grid(column=0, row=9)

        # third queestion: "What study program are you currently following?" + entry to type answer
        self.label_program = ctk.CTkLabel(self.frame, text="What study program are you currently following?",
                                          font=large_font)
        self.label_program.grid(row=10, column=0, padx=10, pady=10, sticky="w")
        self.entry_program = ctk.CTkEntry(self.frame, font=large_font, width=self.master.width / 2,
                                          text_color="#FFCC70", bg_color="#5A5A5A")
        self.entry_program.grid(row=10, column=1, padx=10, pady=10)

        ############################################################
        # empty space between questions
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=30)
        l0.grid(column=0, row=11)

        # fourth question: "Have you followed a university (modal/epistemic) logic course?"
        self.label_course = ctk.CTkLabel(self.frame, text='Have you followed a university modal/epistemic logic '
                                                          'course or a game theory course? \n(If not sure, please '
                                                          'select "Other" and briefly describe course content) ',
                                         font=large_font, anchor='w', justify="left")
        self.label_course.grid(row=12, column=0, padx=10, pady=10, sticky="w")

        # 3 options: Yes, No and Other; if "Other" is selected, then a text box is displayed
        self.course_var = ctk.StringVar()
        course_options = ["Yes", "No", "Other"]
        row_counter = 12
        self.course_option_widgets = []
        for option in course_options:
            row_counter += 1
            entry_other = ctk.CTkTextbox(self.frame, font=large_font, width=self.master.width / 2, height=75,
                                         text_color="#FFCC70", scrollbar_button_color="#4158D0",
                                         scrollbar_button_hover_color="#C850C0")
            entry_other.grid(row=row_counter, column=1, padx=10, pady=10, sticky="w")
            entry_other.grid_forget()  # Initially hide the text box

            radio_button = ctk.CTkRadioButton(self.frame, text=option, variable=self.course_var, value=option,
                                              font=large_font, command=lambda: self.show_other(entry_other),
                                              fg_color="#4158D0", hover_color="#C850C0")
            radio_button.grid(row=row_counter, column=1, padx=10, pady=5, sticky="w")
            self.course_option_widgets.append((radio_button, entry_other))

        ###########################################################
        # back button to go to the previous page
        self.back_button = ctk.CTkButton(self.frame, text="Back", command=self.app.show_previous_page, font=large_font,
                                         fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.back_button.grid(row=17, column=0, padx=10, pady=20, sticky="e")

        # submit button to go to the next page
        self.submit_button = ctk.CTkButton(self.frame, text="Next", command=self.submit_form, font=large_font,
                                           fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.submit_button.grid(row=17, column=1, padx=10, pady=20, sticky="w")

    def show_other(self, entry_other):
        """
        Logic for selecting an answer for the fourth question: if "Other" is selected, then a textbox appears;
        otherwise the textbox disappears
        :param entry_other: textbox object
        """
        # initially hide textbox
        for _, other_entry in self.course_option_widgets:
            other_entry.grid_forget()

        # show the text box if "Other" is selected
        if self.course_var.get() == "Other":
            entry_other.grid(row=16, column=1, padx=10, pady=10, sticky="w")

    def submit_form(self):
        """
        Submit button logic: check that all entries have been filled in, and move to the next page
        """
        # get all answers
        student_rug = self.rug_var.get()
        student_bachelor = self.bsc_var.get()
        study_program = self.entry_program.get()
        logic_course = self.course_var.get()
        additional_info = ""

        # if "Other" is selected, check that an answer has been filled into the textbox
        # if not, show warning and wait
        if logic_course == "Other":
            additional_info = self.course_option_widgets[2][1].get("1.0", "end-1c")
            if additional_info == "":
                self.app.show_warning("Please fill in all entries before continuing")
                return

        # if an entry is empty, show warning and wait
        if student_rug == "" or student_bachelor == "" or study_program == "" or logic_course == "":
            self.app.show_warning("Please fill in all entries before continuing")
        # otherwise, store answers and move to the next page
        else:
            self.app.dict_form_answers_public = self.app.dict_form_answers_public | \
                                                {"Student rug": student_rug, "Student bachelor": student_bachelor,
                                                 "Study program": study_program, "Logic course": logic_course,
                                                 "Logic course (additional)": additional_info}
            self.app.show_next_page()

class Page3:
    def __init__(self, master, app):
        """
        Fourth page displays questions pertaining to the experiment experience
        :param master: the window object
        :param app: the form object
        """
        self.master = master
        self.app = app
        # each page is defined as a frame
        self.frame = ctk.CTkFrame(master, fg_color="#242424")

        # define font size
        large_font = ('Arial', 16)
        extra_large_font = ('Arial', 18)

        # define the title of the page as a label
        self.label_title = ctk.CTkLabel(self.frame, text="Experiment experience (1/2)", font=extra_large_font,
                                        text_color="#FFCC70")
        self.label_title.grid(row=0, column=0, padx=10, pady=10)

        ############################################################################
        # first question: How easy was it to understand the instructions for Cheryl's Puzzle?
        self.label_instructions = ctk.CTkLabel(self.frame, text="How easy was it to understand the instructions for "
                                                                "Cheryl's Puzzle?", font=large_font)
        self.label_instructions.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # slider on a scale from 1 to 10, with text labels for the extrema
        self.slider_instructions = ctk.CTkSlider(self.frame, from_=1, to=10, width=self.master.width / 2,
                                                 number_of_steps=9, fg_color="#4158D0", progress_color="#C850C0",
                                                 button_hover_color="#FFCC70", command=self.slide_instructions)
        self.slider_instructions.grid(row=1, column=1, padx=10, pady=10)

        self.slider_left_instructions = ctk.CTkLabel(self.frame, text='"I had great trouble \nunderstanding"',
                                                     font=large_font, text_color="#FFCC70", justify="left")
        self.slider_left_instructions.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.slider_right_instructions = ctk.CTkLabel(self.frame, text='"I understood \nimmediately"',
                                                      font=large_font, text_color="#FFCC70", justify="right")
        self.slider_right_instructions.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        self.track_slider_instructions = ctk.CTkLabel(self.frame, text=str(int(self.slider_instructions.get())),
                                                      font=extra_large_font)
        self.track_slider_instructions.grid(row=2, column=1, padx=10, pady=10)

        ############################################################################
        # empty space between questions
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=30)
        l0.grid(column=0, row=3)

        # second questions: "Had you heard of Cheryl\'s (Birthday) Puzzle or a similiar puzzle prior to the experiment?"
        self.label_puzzle = ctk.CTkLabel(self.frame, text='Had you heard of Cheryl\'s (Birthday) Puzzle or a similiar '
                                                          'puzzle prior to the experiment? \n(If not sure, please '
                                                          'select "Other" and briefly describe puzzle) ',
                                         font=large_font, anchor='w', justify="left")
        self.label_puzzle.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        # 3 options: Yes, No and Other; if "Other" is selected, then a text box is displayed
        self.puzzle_var = ctk.StringVar()
        puzzle_options = ["Yes", "No", "Other"]
        row_counter = 4
        self.puzzle_option_widgets = []
        for option in puzzle_options:
            row_counter += 1
            entry_other = ctk.CTkTextbox(self.frame, font=large_font, width=self.master.width / 2, height=75,
                                         text_color="#FFCC70", scrollbar_button_color="#4158D0",
                                         scrollbar_button_hover_color="#C850C0")
            entry_other.grid(row=row_counter, column=1, padx=10, pady=10, sticky="w")
            entry_other.grid_forget()  # Initially hide the text box

            radio_button = ctk.CTkRadioButton(self.frame, text=option, variable=self.puzzle_var, value=option,
                                              font=large_font, command=lambda: self.show_other(entry_other),
                                              fg_color="#4158D0", hover_color="#C850C0")
            radio_button.grid(row=row_counter, column=1, padx=10, pady=5, sticky="w")
            self.puzzle_option_widgets.append((radio_button, entry_other))

        ############################################################################
        # empty space between questions
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=30)
        l0.grid(column=0, row=9)

        # third question: "On average, how much did you enjoy the puzzles?"
        self.label_enjoy = ctk.CTkLabel(self.frame, text="On average, how much did you enjoy the puzzles?",
                                        font=large_font)
        self.label_enjoy.grid(row=10, column=0, padx=10, pady=10, sticky="w")

        # slider on a scale from 1 to 10, with text labels for the extrema
        self.slider_enjoy = ctk.CTkSlider(self.frame, from_=1, to=10, width=self.master.width / 2,
                                          number_of_steps=9, fg_color="#4158D0", progress_color="#C850C0",
                                          button_hover_color="#FFCC70", command=self.slide_enjoy)
        self.slider_enjoy.grid(row=10, column=1, padx=10, pady=10)

        self.slider_left_enjoy = ctk.CTkLabel(self.frame, text='"I didn\'t like them \nat all"',
                                              font=large_font, text_color="#FFCC70", justify="left")
        self.slider_left_enjoy.grid(row=11, column=1, padx=10, pady=10, sticky="w")

        self.slider_right_enjoy = ctk.CTkLabel(self.frame, text='"I enjoyed them \ngreatly"',
                                               font=large_font, text_color="#FFCC70", justify="right")
        self.slider_right_enjoy.grid(row=11, column=1, padx=10, pady=10, sticky="e")

        self.track_slider_enjoy = ctk.CTkLabel(self.frame, text=str(int(self.slider_enjoy.get())),
                                               font=extra_large_font)
        self.track_slider_enjoy.grid(row=11, column=1, padx=10, pady=10)

        ############################################################################
        # empty space between questions
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=30)
        l0.grid(column=0, row=12)

        # fourth question: "On average, how difficult did you find the puzzles?"
        self.label_diff = ctk.CTkLabel(self.frame, text="On average, how difficult did you find the puzzles?",
                                       font=large_font)
        self.label_diff.grid(row=13, column=0, padx=10, pady=10, sticky="w")

        # slider on a scale from 1 to 10, with text labels for the extrema
        self.slider_diff = ctk.CTkSlider(self.frame, from_=1, to=10, width=self.master.width / 2,
                                         number_of_steps=9, fg_color="#4158D0", progress_color="#C850C0",
                                         button_hover_color="#FFCC70", command=self.slide_diff)
        self.slider_diff.grid(row=13, column=1, padx=10, pady=10)

        self.slider_left_diff = ctk.CTkLabel(self.frame, text='"I found it \nvery easy"',
                                             font=large_font, text_color="#FFCC70", justify="left")
        self.slider_left_diff.grid(row=14, column=1, padx=10, pady=10, sticky="w")

        self.slider_right_diff = ctk.CTkLabel(self.frame, text='"I found it \nvery difficult"',
                                              font=large_font, text_color="#FFCC70", justify="right")
        self.slider_right_diff.grid(row=14, column=1, padx=10, pady=10, sticky="e")

        self.track_slider_diff = ctk.CTkLabel(self.frame, text=str(int(self.slider_diff.get())),
                                              font=extra_large_font)
        self.track_slider_diff.grid(row=14, column=1, padx=10, pady=10)

        ################################################################################
        # back button to go to the previous page
        self.back_button = ctk.CTkButton(self.frame, text="Back", command=self.app.show_previous_page, font=large_font,
                                         fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.back_button.grid(row=15, column=0, padx=10, pady=20, sticky="e")

        # submit button to go to the next page
        self.submit_button = ctk.CTkButton(self.frame, text="Next", command=self.submit_form, font=large_font,
                                           fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.submit_button.grid(row=15, column=1, padx=10, pady=20, sticky="w")

    def slide_instructions(self, value):
        """
        Logic for the slider for the first question: update a label to display the value currently selected
        :param value: slider value at a moment
        """
        self.track_slider_instructions.configure(text=int(value))

    def slide_enjoy(self, value):
        """
        Logic for the slider for the third question: update a label to display the value currently selected
        :param value: slider value at a moment
        """
        self.track_slider_enjoy.configure(text=int(value))

    def slide_diff(self, value):
        """
        Logic for the slider for the fourth question: update a label to display the value currently selected
        :param value: slider value at a moment
        """
        self.track_slider_diff.configure(text=int(value))

    def show_other(self, entry_other):
        """
        Logic for selecting an answer for the second question: if "Other" is selected, then a textbox appears;
        otherwise the textbox disappears
        :param entry_other: textbox object
        """
        # initially, hide the textbox
        for _, other_entry in self.puzzle_option_widgets:
            other_entry.grid_forget()

        # show the textbox if "Other" is selected
        if self.puzzle_var.get() == "Other":
            entry_other.grid(row=8, column=1, padx=10, pady=10, sticky="w")

    def submit_form(self):
        """
        Submit button logic: check that all entries have been filled in, and move to the next page
        """
        # get all answers
        difficulty_instructions = int(self.slider_instructions.get())
        know_puzzle = self.puzzle_var.get()
        enjoy_puzzle = int(self.slider_enjoy.get())
        difficulty_puzzle = int(self.slider_diff.get())
        additional_info = ""

        # if the "Other" option for the second question was selected, make sure that an answer is filled into the
        # textbox; if not, show warning and wait
        if know_puzzle == "Other":
            additional_info = self.puzzle_option_widgets[2][1].get("1.0", "end-1c")
            if additional_info == "":
                self.app.show_warning("Please fill in all entries before continuing")
                return

        # if entries are left empty, show warning and wait
        if know_puzzle == "":
            self.app.show_warning("Please fill in all entries before continuing")
        # otherwise, store the answers and move to the next page
        else:
            self.app.dict_form_answers_public = self.app.dict_form_answers_public | \
                                                {"Difficulty instructions": difficulty_instructions,
                                                 "Enjoy puzzle": enjoy_puzzle, "Difficulty puzzle": difficulty_puzzle,
                                                 "Know puzzle?": know_puzzle,
                                                 "Know puzzle? (additional)": additional_info}
            self.app.show_next_page()


class Page4:
    def __init__(self, master, app):
        """
        Fifth page displays questions pertaining to the experiment experience
        :param master: the window object
        :param app: the form object
        """
        self.master = master
        self.app = app
        # each page is defined as a frame
        self.frame = ctk.CTkFrame(master, fg_color="#242424")

        # define font size
        large_font = ('Arial', 16)

        # define title of page as label
        self.label_title = ctk.CTkLabel(self.frame, text="Experiment experience (2/2)", font=('Arial', 18),
                                        text_color="#FFCC70")
        self.label_title.grid(row=0, column=0, padx=10, pady=10)

        ############################################################################
        # first question: "Briefly, please describe the strategies you used to solve Cheryl\'s Puzzle  (if any)
        # and how these strategies evolved with practice." + entry to write the answer
        self.label_strategy = ctk.CTkLabel(self.frame, text='Briefly, please describe the strategies you used to solve '
                                                            'Cheryl\'s Puzzle  (if any) \nand how these strategies '
                                                            'evolved with practice.',
                                           font=large_font, anchor='w', justify="left")
        self.label_strategy.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.entry_strategy = ctk.CTkTextbox(self.frame, font=large_font, width=self.master.width / 2, height=75,
                                             text_color="#FFCC70", scrollbar_button_color="#4158D0",
                                             scrollbar_button_hover_color="#C850C0")
        self.entry_strategy.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ############################################################################
        # empty space between questions
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=30)
        l0.grid(column=0, row=2)

        # second question: "Please rate your mood today."
        self.label_mood = ctk.CTkLabel(self.frame, text="Please rate your mood today.",
                                       font=large_font)
        self.label_mood.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        # slider on a scale from 1 to 10, with text labels for the extrema
        self.slider_mood = ctk.CTkSlider(self.frame, from_=1, to=10, width=self.master.width / 2,
                                         number_of_steps=9, fg_color="#4158D0", progress_color="#C850C0",
                                         button_hover_color="#FFCC70", command=self.slide_mood)
        self.slider_mood.grid(row=3, column=1, padx=10, pady=10)

        self.slider_left_mood = ctk.CTkLabel(self.frame, text='"I feel very sad"',
                                             font=large_font, text_color="#FFCC70", justify="left")
        self.slider_left_mood.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        self.slider_right_mood = ctk.CTkLabel(self.frame, text='"I feel very happy"',
                                              font=large_font, text_color="#FFCC70", justify="right")
        self.slider_right_mood.grid(row=4, column=1, padx=10, pady=10, sticky="e")

        self.track_slider_mood = ctk.CTkLabel(self.frame, text=str(int(self.slider_mood.get())),
                                              font=large_font)
        self.track_slider_mood.grid(row=4, column=1, padx=10, pady=10)

        ##############################################################################
        # empty space between questions
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=30)
        l0.grid(column=0, row=5)

        # third question: "Any final remarks? (optional)" + entry to write answer
        self.label_remark = ctk.CTkLabel(self.frame, text='Any final remarks? (optional)',
                                         font=large_font, anchor='w', justify="left")
        self.label_remark.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        self.entry_remark = ctk.CTkTextbox(self.frame, font=large_font, width=self.master.width / 2, height=100,
                                           text_color="#FFCC70", scrollbar_button_color="#4158D0",
                                           scrollbar_button_hover_color="#C850C0")
        self.entry_remark.grid(row=6, column=1, padx=10, pady=10, sticky="w")

        ###############################################################################
        # back button to go to the previous page
        self.back_button = ctk.CTkButton(self.frame, text="Back", command=self.app.show_previous_page, font=large_font,
                                         fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.back_button.grid(row=7, column=0, padx=10, pady=20, sticky="e")

        # submit button to move to the next page
        self.submit_button = ctk.CTkButton(self.frame, text="Submit form", command=self.submit_form, font=large_font,
                                           fg_color="#4158D0", hover_color="#C850C0", corner_radius=32)
        self.submit_button.grid(row=7, column=1, padx=10, pady=20, sticky="w")

    def slide_mood(self, value):
        """
        Logic for the slider for the second question: update a label to display the value currently selected
        :param value: slider value at a moment
        """
        self.track_slider_mood.configure(text=int(value))

    def submit_form(self):
        """
        Submit button logic: check that all entries have been filled in, and move to the next page
        """
        # get all answers
        strategy = self.entry_strategy.get("1.0", "end-1c")
        mood = int(self.slider_mood.get())
        remarks = self.entry_remark.get("1.0", "end-1c")

        # if entry is left empty, show warning and wait
        if strategy == "":
            self.app.show_warning("Please fill in all entries before continuing")
        # otherwise, store answers and move to the next page
        else:
            self.app.dict_form_answers_public = self.app.dict_form_answers_public | \
                                                {"Strategy": strategy, "Mood": mood, "Remarks": remarks}
            self.save_data()
            self.app.show_next_page()

    def save_data(self):
        """
        Save all answers as csv
        """
        # save the private information separately
        df_private_info = pd.DataFrame([self.app.dict_form_answers_private])
        df_private_info.to_csv(f"Contact info_{self.app.subject_id}.csv", index=False)

        # merge the non-private information with the puzzle answers and save together in one csv
        temp_dict_form_answers = [self.app.dict_form_answers_public] * len(self.app.dict_puzzle_answers)
        temp_all_answers = [self.app.dict_puzzle_answers[i] | temp_dict_form_answers[i]
                            for i in range(len(self.app.dict_puzzle_answers))]
        df_all_answers = pd.DataFrame(temp_all_answers)
        df_all_answers.to_csv(f"All answers_{self.app.subject_id}.csv", index=False)


class Page5:
    def __init__(self, master, app):
        """
        Last page displays a thank-you message
        :param master: the window object
        :param app: the form object
        """
        self.master = master
        self.app = app
        # each page is defined as frame
        self.frame = ctk.CTkFrame(master, fg_color="#242424")

        # define font size
        large_font = ('Arial', 16)

        # empty space such that text is displayed in the middle of the screen
        l0 = ctk.CTkLabel(self.frame, text=" ", width=3, height=self.master.width / 6)
        l0.grid(column=0, row=0)

        # for convenience, the thank-you message is read in from a txt file
        f = open(f"text/background_form_outro.txt", "r")
        intro_text = f.read()
        f.close()

        ############################################################################
        # the thank-you message is displayed as a label
        self.label_title = ctk.CTkLabel(self.frame, text=intro_text, font=('Arial', 18), text_color="#FFCC70",
                                        width=self.master.width)
        self.label_title.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")


if __name__ == "__main__":
    # for testing purposes; normally called from quickstart.py
    root = Window("User Information Form")
    app = FormApp(root)
    root.mainloop()
