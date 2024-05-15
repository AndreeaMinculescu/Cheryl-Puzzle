# Credits: https://github.com/jdtoprug/EpistemicToMProject

import pandas as pd
from puzzle_formalism import Puzzle
from epistemic_model import EpistemicModel
import os
import math

################## MODEL PREDICTIONS ##################


def get_prediction_one_model(solver, kwargs):
    """
    Given a solver and specific properties, solve the puzzle and return the answer

    :param solver: the solver object
    :param kwargs: arguments for the run_model_once function implemented for all solvers
    :return: the answer given by the solver
    """
    graph = solver.generate_full_model()
    model_answer = solver.run_model_once(graph, **kwargs)
    # remove inconsistencies in naming for the month September
    return model_answer.replace("Sept", "September")


def generate_all_predictions(max_pa_tom_level=3):
    """
    Generates file with all ToM models' predictions for the answers of the human participants

    :param max_pa_tom_level: the maximum possible level of ToM for public announcements
    """
    # read in subject data
    subj_df = pd.read_csv("../analysis/All answers_puzzles.csv")
    # read in question bank
    questions_df = pd.read_csv("../interface/question_bank.csv")
    # initialize prediction dataframe
    predictions_df = pd.DataFrame(columns=["Subject.id", "Trial", "ToM.level", "Correct.answer", "Subject.answer",
                                           "Is.subject.correct", "Model.predictions", "Is.model.correct"])
    # initialize puzzle object
    cb = Puzzle(list_players=["Al", "Be"], visibility=[[True, False], [False, True]])

    # for each data entry
    for idx, row in subj_df.iterrows():
        # get the correct answer to the current puzzle
        correct_answer = questions_df["Translated answer"].loc[questions_df["IDX"] == row["Index"]].values[0]

        model_predictions = []
        model_is_correct = []

        # initialize epistemic model
        temp_solver = EpistemicModel(1, max_pa_tom_level, row["Level"] - 1, cb)
        # model_level is defined as the maximum level of ToM that the model can process; the model cuts off operators
        # in statements with higher ToM level than model_level, until the statement reaches model_level ToM
        # note: model_level = 0 means that cutting is disabled
        for model_level in range(max_pa_tom_level):
            for model_cutting_dir in ["lr", "rl"]:
                if model_level == 0 and model_cutting_dir == "rl":
                    continue
                # get the answer predicted by the model
                model_answer = get_prediction_one_model(temp_solver, {"model_level": model_level,
                                                                      "cutting_direction": model_cutting_dir})
                # store the prediction
                model_predictions.append(model_answer)
                # determine whether the predicted answer is the correct answer
                model_is_correct.append(bool(model_answer == correct_answer))

        predictions_df.loc[predictions_df.shape[0]] = [row["Subject.id"], row["Trial"], row["Level"], correct_answer,
                                                       row["Translated.answer"], bool(row["Is.correct"]),
                                                       model_predictions, model_is_correct]

    predictions_df.reset_index(drop=True, inplace=True)
    predictions_df.to_csv("predictions_tom.csv", index=False)

################## MODEL EVIDENCE ##################


def get_accuracy(answer_bool_list):
    """
    Compute accuracy as follows:
        the number of correct answer/the total number of answers

    :param answer_bool_list: list of booleans where answer_bool_list[i] is True if the i-th answer is correct
    and False otherwise
    :return: the accuracy value
    """
    return sum(answer_bool_list) / len(answer_bool_list)


def count_common_answers(subj_answers, model_answers):
    """
    Count how many answers predicted by the model are the same as the participant's answers

    :param subj_answers: list of a participant's answer
    :param model_answers: list of answers predicted by the model for that participant
    :return: the number of answers predicted by the model that correspond with the participant's answers
    """
    count_same_answer = 0
    for idx in range(len(subj_answers)):
        if subj_answers[idx] == model_answers[idx]:
            count_same_answer += 1
    return count_same_answer


def count_subject_answers(answer_list):
    """
    Given a list of a participant's answers, count how many times each unique answer occurred

    :param answer_list: the list of a participant's answers
    :return: dictionary where the keys are unique answers and the values are the occurrences
    """
    dict_ans = {}

    for ans in answer_list:
        try:
            dict_ans[ans] += 1
        except KeyError:
            dict_ans[ans] = 1
    return dict_ans


# function adapted from https://github.com/jdtoprug/EpistemicToMProject
def compute_likelihood(correct, incorrect, penalty=0.5):
    """
    Calculate log-likelihood

    :param correct: number of times model predictions corresponded to participant answers
    :param incorrect: number of times model predictions deviated from participant answers
    :param penalty: p in n(1-e)*ln(1-e) + ne*ln(pe)
    :return: log-likelihood of participant using this model's strategy
    """
    # epsilon, error rate - incoherent answers divided by n
    e = incorrect / (correct + incorrect)
    likelihood = 0
    if correct > 0:
        likelihood += correct * math.log(1 - e)  # n(1-e)*ln(1-e)
    if incorrect > 0:
        likelihood += incorrect * math.log(e * penalty)  # ne*ln(pe)
    return likelihood


# function adapted from https://github.com/jdtoprug/EpistemicToMProject
def compute_error_likelihood_random(answer_dict):
    """
    Calculates likelihood for random model, taking into account the participant's answer distribution

    :param answer_dict: dictionary where the keys are unique answers given by the participant and the values are the
    occurrences
    :return: log-likelihood of random model corresponding to participant
    """
    likelihood = 0  # To-be-outputted log-likelihood
    n = sum(answer_dict.values())  # Calculate n, the total number of decision points
    for count_ans in answer_dict.values():  # Loop over answers
        likelihood += (count_ans * math.log(count_ans / n))  # Sum over answers of a*ln(a/n)
    return likelihood


def compute_correct_rate_random(answer_dict):
    """
    Calculates coherence for random model, taking into account the participant's answer distribution

    :param answer_dict: dictionary where the keys are unique answers given by the participant and the values are the
    occurrences
    :return: proportion of times random model should correspond to participant
    """
    n = sum(answer_dict.values())  # Total number of answers given
    rate = sum([ans * (ans/n) for ans in answer_dict.values()]) / n
    return rate


def generate_log_likelihoods(name_pred_file="predictions_tom"):
    """
    Computes evidence for each model and saves to file

    :param name_pred_file: file path where all model predictions for participants' answers have been saved
    """
    # if the predictions file does not exist, then first generate it
    if not os.path.exists(f"{name_pred_file}.csv"):
        generate_all_predictions()
    # load the prediction file
    prediction_model_df = pd.read_csv(f"{name_pred_file}.csv")

    # initialize dataframe for model evidence
    likelihood_df = pd.DataFrame(columns=["Subject.id", "Model.idx", "Log-likelihood", "Correct/Total",
                                          "Subject.accuracy", "Model.accuracy"])

    # for each participant
    for subj_id in set(prediction_model_df["Subject.id"]):
        # retrieve the list of given answers
        subj_answers = prediction_model_df["Subject.answer"].loc[
            prediction_model_df["Subject.id"] == subj_id].values
        # retrieve which answers were correct and which incorrect
        subj_bool_answers = prediction_model_df["Is.subject.correct"].loc[
            prediction_model_df["Subject.id"] == subj_id].values
        # compute accuracy for the current participant
        subj_accuracy_score = get_accuracy(subj_bool_answers)

        # retrieve all the answers predicted by all models
        all_models_answers = [eval(x) for x in prediction_model_df["Model.predictions"].loc[
            prediction_model_df["Subject.id"] == subj_id].values]
        # retrieve which answers were correct and which incorrect for all models
        all_models_bool_answers = [eval(x) for x in prediction_model_df["Is.model.correct"].loc[
            prediction_model_df["Subject.id"] == subj_id].values]
        # iterate through all ToM models
        for model_idx in range(len(eval(prediction_model_df["Model.predictions"][0]))):
            # extract all the answers predicted by the current model
            model_answers = [x[model_idx] for x in all_models_answers]
            # extract which answers were correct and which incorrect for the current model
            model_bool_answers = [x[model_idx] for x in all_models_bool_answers]

            # compute the current model's accuracy
            model_accuracy_score = get_accuracy(model_bool_answers)
            # find how many answers were correctly predicted by the model, relative to the answers given by the
            # current participant
            number_same_answer = count_common_answers(subj_answers, model_answers)
            # compute the log-likelihood that the current participants used the current model's strategy
            likelihood = compute_likelihood(number_same_answer, len(model_answers) - number_same_answer)
            # store data
            likelihood_df.loc[likelihood_df.shape[0]] = [subj_id, model_idx, likelihood,
                                                         number_same_answer/len(model_answers), subj_accuracy_score,
                                                         model_accuracy_score]

        # count the number of occurrences for each unqiue answer for the current participant
        dict_count_subj_answers = count_subject_answers(subj_answers)
        # compute the log-likelihood that the current participants used random model's strategy, given the distribution
        # of answers for that participant
        likelihood_random = compute_error_likelihood_random(dict_count_subj_answers)
        # compute the coherence of the random model
        coherence_random = compute_correct_rate_random(dict_count_subj_answers)
        # store data
        likelihood_df.loc[likelihood_df.shape[0]] = [subj_id, model_idx+1, likelihood_random, "", subj_accuracy_score,
                                                     coherence_random]

    likelihood_df.reset_index(drop=True, inplace=True)
    likelihood_df.to_csv("likelihoods.csv", index=False)


if __name__ == "__main__":
    generate_log_likelihoods()
