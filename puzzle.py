import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from window import Window
from PIL import Image
import random
import time
import pandas as pd


def minutes_to_milliseconds(orig_time):
    """
    Transform minutes into milliseconds
    :param orig_time: the original time in minutes
    :return: the transformed time in milliseconds
    """
    return orig_time * 60_000


def milliseconds_to_minutes(orig_time):
    """
    Transform milliseconds into minute
    :param orig_time: the original time in milliseconds
    :return: the transformed time in minutes
    """
    return int(orig_time / 60_000)


# global timer and intermediate warnings
time_out = minutes_to_milliseconds(45)  # 45 mins in milliseconds
# time_out = 30_000
first_warning = minutes_to_milliseconds(30)  # 30 mins passed
# first_warning = 20_000
second_warning = minutes_to_milliseconds(40)  # 40 mins passed
previous_warnings = []


def format_instruction_text(dict_options, dialogue, scenario):
    """
    Format instruction text such that the standard text is merged with the question bank
    :param dict_options: answer options from the question bank
    :param dialogue: dialogue between Albert and Bernard from the question bank
    :param scenario: type of scenario
    :return: the formatted instruction text
    """
    f = open(f"text/{scenario}.txt", "r")
    text = f.read().split("; ")
    f.close()
    instruction_text = text[0]

    for option in dict_options.keys():
        instruction_text += f'\n\u2022 {option}: {",".join([str(elem) for elem in dict_options[option]])}'

    instruction_text += f'\n{text[1]}'

    list_dialogue = dialogue.split('; ')
    for line in list_dialogue:
        instruction_text += f'\n{line}'

    instruction_text += text[2]
    return instruction_text


class PuzzleApp:
    def __init__(self, master, question_idx, question_count, no_puzzles, answers_list, start_time):
        """
        Class that manages the display of the puzzles
        :param master: the window object
        :param question_idx: the current index of the question in the question bank
        :param question_count: the current question count
        :param no_puzzles: total number of puzzles
        :param answers_list: array to store answers in
        :param start_time: the time the current puzzle was first displayed; used to compute how long solving a puzzle takes
        """
        self.master = master
        # store question bank

        self.all_answers = answers_list
        self.start_time = start_time
        self.after_first_warning = None
        self.after_second_warning = None
        self.after_time_out = None

        self.question_idx = question_idx
        self.question_count = question_count + 1
        self.no_puzzles = no_puzzles

        if self.question_count == int(self.no_puzzles/2)+1:
            self.show_pbeauty()
        else:
            if self.question_count > int(self.no_puzzles/2)+1:
                self.question_count -= 1
            self.show_puzzle()

####################### Puzzle interface #######################
    def show_puzzle(self):
        """
        Define objects on the puzzle interface
        """
        # read in all puzzle questions
        self.question_bank = pd.read_csv("question_bank.csv")
        # get puzzle options for the current puzzle
        self.puzzle_options = eval(self.question_bank['Options'][self.question_idx])
        # get the scenario for the current puzzle
        self.puzzle_scenario = self.question_bank['Scenario'][self.question_idx]
        # get the text for the current puzzle
        self.puzzle_text = format_instruction_text(self.puzzle_options,
                                                   self.question_bank['Dialogue'][self.question_idx],
                                                   scenario=self.puzzle_scenario)
        self.puzzle_text = f"If applicable, remember to discard the piece of paper used to take notes for the " \
                           f"previous puzzle. You may now use the next piece of paper. \nPuzzle " \
                           f"{self.question_count}/{self.no_puzzles}: \n\n" + self.puzzle_text

        ###################################################
        # text label for puzzle puzzle text
        self.label_text = ctk.CTkTextbox(self.master, font=('Arial', 18), height=self.master.height / 2,
                                         width=self.master.width, state="normal", text_color="#FFCC70",
                                         wrap=ctk.WORD, scrollbar_button_color="#4158D0",
                                         scrollbar_button_hover_color="#C850C0")
        self.label_text.insert(ctk.END, self.puzzle_text)
        self.label_text.configure(state="disabled")
        self.label_text.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w")

        #####################################################
        # add Submit Answer text in front of the drop-down menu
        self.label_select = ctk.CTkLabel(self.master, text="Select Answer:", width=13, font=("arial", 20))
        self.label_select.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        #########################################################
        # display answer option in a drop-down menu
        list_of_options = [f"{item[0]}, {day}" for item in self.puzzle_options.items() for day in item[1]]
        random.shuffle(list_of_options)
        list_of_options.extend(["No solution", "Multiple solutions"])
        combobox_var = ctk.StringVar(value="I don't know")
        self.drplist = ctk.CTkComboBox(self.master, values=list_of_options, state='readonly',
                                       dropdown_fg_color="#4158D0",
                                       corner_radius=32, variable=combobox_var, width=235)
        self.drplist.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ##########################################################
        # display an image representative for the scenario (for aesthetic purposes only)
        img = ctk.CTkImage(light_image=Image.open(f'img/{self.puzzle_scenario}.png'), size=(300, 300))
        self.image_panel = ctk.CTkLabel(master=self.master, image=img, text='')
        self.image_panel.grid(row=2, column=2)

        ##############################################################
        # submit button display and logic: once clicked, store the correct answer and the time from start_time to the click
        self.submit_button = ctk.CTkButton(self.master, text='Submit', corner_radius=32, fg_color="#4158D0",
                                           hover_color="#C850C0", width=120, height=32, command=self.clicked)
        self.submit_button.grid(row=2, column=0, pady=20)

        ##############################################################
        # show warnings after pre-specified amounts of time
        self.after_first_warning = self.master.after(first_warning, lambda: self.show_warning(
            milliseconds_to_minutes(time_out - first_warning)))
        self.after_second_warning = self.master.after(second_warning, lambda: self.show_warning(
            milliseconds_to_minutes(time_out - second_warning)))

        # after a pre-specified amount of time, end experiment by killing the window
        self.after_time_out = self.master.after(time_out, self.remove_all_objects)

    @staticmethod
    def show_warning(remaining_time):
        """
        Format time warning
        :param remaining_time: time left until experiment is over
        """
        global previous_warnings
        if remaining_time not in previous_warnings:
            # make sure each warning is shown once
            previous_warnings.append(remaining_time)
            # display warning in a message box
            msg = CTkMessagebox(title="Warning", message=f"You have {remaining_time} minutes left",
                                icon="img/warning.png")
            # if the message is not closed manually, it disappears after 10 seconds
            msg.after(10_000, msg.destroy)

    def remove_all_objects(self):
        """
        Destroy all objects on the page and quit window
        """
        self.label_text.destroy()
        self.submit_button.destroy()
        self.image_panel.destroy()
        self.label_select.destroy()
        self.drplist.destroy()

        self.master.quit()

    def clicked(self):
        """
        Submit button logic: store the correct answer and the time from start_time to the click, delete text labels and
        button, quit window
        """
        answer = self.drplist.get()
        self.all_answers[-1]["Given answer"] = answer
        self.all_answers[-1]["Time"] = time.time() - self.start_time

        self.remove_all_objects()

####################### P-beauty interface #######################
    def show_pbeauty(self):
        """
        Define objects on the p-beauty contest interface
        """
        # define font size
        large_font = ('Arial', 16)

        # empty space such that text is displayed in the middle of the screen
        l0 = ctk.CTkLabel(self.master, text=" ", width=3, height=self.master.width / 8)
        l0.grid(column=0, row=0)

        # for convenience, the p-beauty instructions are read in from a txt file
        f = open(f"text/p-beauty.txt", "r")
        intro_text = f.read()
        f.close()

        ############################################################################
        # the p-beauty instructions are displayed as a label
        self.label_instructions = ctk.CTkLabel(self.master, text=intro_text, font=('Arial', 18), text_color="#FFCC70",
                                               width=self.master.width)
        self.label_instructions.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        ###########################################################################
        # empty space such that text is displayed in the middle of the screen
        l0 = ctk.CTkLabel(self.master, text=" ", width=3, height=self.master.width / 6)
        l0.grid(column=0, row=2)

        # slider on a scale from 1 to 10, with text labels for the current value
        self.slider_instructions = ctk.CTkSlider(self.master, from_=1, to=100, width=self.master.width / 2,
                                                 number_of_steps=99, fg_color="#4158D0", progress_color="#C850C0",
                                                 button_hover_color="#FFCC70", command=self.slide_instructions)
        self.slider_instructions.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.track_slider_instructions = ctk.CTkLabel(self.master, text=str(int(self.slider_instructions.get())),
                                                      font=large_font)
        self.track_slider_instructions.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        ##############################################################################
        # submit button to continue to the next page
        self.submit_button = ctk.CTkButton(self.master, text="Submit", command=self.submit_form, font=large_font,
                                           fg_color="#4158D0", hover_color="#C850C0", corner_radius=32, width=10)
        self.submit_button.grid(row=5, column=1, pady=20, sticky="w")

    def slide_instructions(self, value):
        """
        Logic for the slider for the first question: update a label to display the value currently selected
        :param value: slider value at a moment
        """
        self.track_slider_instructions.configure(text=int(value))

    def submit_form(self):
        """
        Submit button logic: check that all entries have been filled in, and move to the next page
        """
        # get all answers
        p_beauty_number = int(self.slider_instructions.get())

        self.all_answers[-1]["Given answer"] = p_beauty_number
        self.all_answers[-1]["Time"] = time.time() - self.start_time

        self.label_instructions.destroy()
        self.slider_instructions.destroy()
        self.submit_button.destroy()
        self.master.quit()


if __name__ == "__main__":
    # for testing purposes; normally called from quickstart.py
    root = Window("Cheryl's Puzzle")
    app = PuzzleApp(root, 0, 0, 5, [], time.time())
    root.mainloop()
