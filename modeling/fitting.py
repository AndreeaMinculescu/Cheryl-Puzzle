# Credits: https://github.com/jdtoprug/EpistemicToMProject

import pandas as pd
from puzzle_formalism import Puzzle
from epistemic_model import EpistemicModel
import os
import math
import scipy
import itertools
from utilities import plot_bar
from collections import Counter

CONFIG = "test"
NAME_BAR_PLOT = f"plots/metadata/distribChosen_{CONFIG}"
SUBJ_MODEL_FILE_PATH = f"plots/metadata/{CONFIG}"
SAVE_BOOL = False
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


def generate_all_predictions(name_predictions_file="predictions_tom", max_pa_tom_level=3):
    """
    Generates file with all ToM models' predictions for the answers of the human participants

    :param max_pa_tom_level: the maximum possible level of ToM for public announcements
    """
    # read in subject data
    subj_df = pd.read_csv("../analysis/All answers_puzzles.csv")
    # uncomment below to only process wrong answers; change to value 1 for only correct answers
    # subj_df = subj_df.loc[(subj_df["Is.correct"] == 0)]
    # uncomment and adjust below to only process certain levels of ToM
    # subj_df = subj_df.loc[(subj_df["Level"] > 2)]
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
        model_cutting_dirs_config = ["lr", "rl"]

        # initialize epistemic model
        temp_solver = EpistemicModel(1, max_pa_tom_level, row["Level"] - 1, cb)
        # model_level is defined as the maximum level of ToM that the model can process; the model cuts off operators
        # in statements with higher ToM level than model_level, until the statement reaches model_level ToM
        # note: model_level = 0 means that cutting is disabled
        for model_level in range(max_pa_tom_level):
            for model_cutting_dir in model_cutting_dirs_config:
                # for epistemic model (model_level=0) compute answer only once (model_cutting_dir has no effect;
                # for cut-2 model (model_level=2), only cut from left or from right (both give the same answer)
                if model_level in [0, 2] and model_cutting_dir != model_cutting_dirs_config[0]:
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
    predictions_df.to_csv(f"{name_predictions_file}.csv", index=False)

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
def compute_likelihood(correct, incorrect, penalty=1/12):
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
def compute_error_likelihood_random(subj_answer_dict, name_pred_file):
    """
    Calculates likelihood for random model, taking into account the participant's answer distribution

    :param answer_dict: dictionary where the keys are unique answers given by the participant and the values are the
    occurrences
    :return: log-likelihood of random model corresponding to participant
    """
    pred_df = pd.read_csv(f'{name_pred_file}.csv')
    all_subj_answer_dict = {}
    for ans in list(pred_df["Subject.answer"]):
        try:
            all_subj_answer_dict[ans] += 1
        except KeyError:
            all_subj_answer_dict[ans] = 1

    likelihood = 0
    for ans in subj_answer_dict.keys():
        likelihood += subj_answer_dict[ans] * math.log(all_subj_answer_dict[ans]/sum(all_subj_answer_dict.values()))
    return likelihood

def compute_likelihood_random_2(subj_answers, penalty=1/12):
    """
    Calculate log-likelihood

    :param correct: number of times model predictions corresponded to participant answers
    :param incorrect: number of times model predictions deviated from participant answers
    :param penalty: p in n(1-e)*ln(1-e) + ne*ln(pe)
    :return: log-likelihood of participant using this model's strategy
    """
    epsilon = max(dict(Counter(subj_answers)).values())/len(subj_answers)
    likelihood = 0
    if 1 - epsilon > 0:
        likelihood += len(subj_answers) * (1 - epsilon) * math.log(1 - epsilon)  # n(1-e)*ln(1-e)
    if epsilon > 0:
        likelihood += len(subj_answers) * epsilon * math.log(penalty * epsilon)  # ne*ln(pe)
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


def generate_log_likelihoods(name_likelihood_file="likelihoods", name_pred_file="predictions_tom", replace_all=False):
    """
    Computes evidence for each model and saves to file

    :param name_pred_file: file path where all model predictions for participants' answers have been saved
    """
    # if the predictions file does not exist, then first generate it
    if not os.path.exists(f"{name_pred_file}.csv") or replace_all:
        generate_all_predictions(name_predictions_file=name_pred_file)
    # load the prediction file
    prediction_model_df = pd.read_csv(f"{name_pred_file}.csv")

    # initialize dataframe for model evidence
    likelihood_df = pd.DataFrame(columns=["Subject.id", "Model.idx", "Log-likelihood", "Correct.rate",
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
        likelihood_random = compute_error_likelihood_random(dict_count_subj_answers, name_pred_file)
        # compute the coherence of the random model
        coherence_random = compute_correct_rate_random(dict_count_subj_answers)
        # store data
        likelihood_df.loc[likelihood_df.shape[0]] = [subj_id, model_idx+1, likelihood_random, coherence_random,
                                                     subj_accuracy_score, ""]

    likelihood_df.reset_index(drop=True, inplace=True)
    likelihood_df.to_csv(f"{name_likelihood_file}.csv", index=False)


################## RFX-BMS ##################

# function adapted from https://github.com/jdtoprug/EpistemicToMProject
def get_best_models_for_each_subj(name_likelihood_file="likelihoods", name_pred_file="predictions_tom",
                                  replace_all=False):
    """
    For each participant, find the model with the best correct rate.

    :param name_likelihood_file: the path to the likelihoods csv file
    :param name_pred_file: the path the predictions csv file
    :return: a dict storing the likelihoods for each subject-model pair
    """
    if not os.path.exists(f"{name_likelihood_file}.csv") or replace_all:
        generate_log_likelihoods(name_likelihood_file=name_likelihood_file, name_pred_file=name_pred_file,
                                 replace_all=replace_all)
    pred_df = pd.read_csv(f"{name_pred_file}.csv")
    likelihood_df = pd.read_csv(f"{name_likelihood_file}.csv")

    if SAVE_BOOL:
        file = open(f"{SUBJ_MODEL_FILE_PATH}.txt", "w")

    likelihoods_dict = {}
    correct_rates_dict = {}
    # extract relevant information from the likelihood dataframe
    for idx, row in likelihood_df.iterrows():
        likelihoods_dict[(row[0], row[1])] = row[2]
        correct_rates_dict[(row[0], row[1])] = row[3]

    all_best_correct_rates = []
    best_correct_rates_per_model = [[] for _ in set(likelihood_df["Model.idx"])]
    number_choices_best_per_model = {idx:0 for idx in set(likelihood_df["Model.idx"])}
    # get and store the model(s) with the best correct rate for each participant
    for subj_idx, subj in enumerate(set(likelihood_df["Subject.id"])):
        best_correct_rate = 0
        best_models = []

        for model_id in set(likelihood_df["Model.idx"]):
            curr_correct_rate = correct_rates_dict[(subj, model_id)]
            if curr_correct_rate > best_correct_rate:
                best_correct_rate = curr_correct_rate
                best_models = [model_id]
            elif curr_correct_rate == best_correct_rate:
                best_models.append(model_id)

        all_best_correct_rates.append(best_correct_rate)

        for m in best_models:
            best_correct_rates_per_model[m].append(best_correct_rate)
            number_choices_best_per_model[m] += 1/len(best_models)

        if SAVE_BOOL:
            file.write(f"{subj_idx}, {subj}\n")
            file.write(f"{pred_df['Subject.answer'].loc[pred_df['Subject.id'] == subj].values}\n")
            file.write(f"\t best correct rate: {best_correct_rate}\n")
            file.write(f"\t best models: {best_models}\n")
            file.write("\n")

    if SAVE_BOOL:
        file.close()
        plot_bar(number_choices_best_per_model, "Frequency of times each model was chosen as best", "Model index",
                 "Frequency", (0, max(number_choices_best_per_model.values())),
                 (min(number_choices_best_per_model.keys()), max(number_choices_best_per_model.keys())),
                 f"{NAME_BAR_PLOT}", rotation_x=0)
    # store the best correct rates per model and all overall best correct rates
    correct_rates_df = pd.concat([pd.DataFrame(best_correct_rates_per_model), pd.DataFrame([all_best_correct_rates])],
                                 sort=False, ignore_index=True).fillna(0)
    correct_rates_df.to_csv("correct_rates.csv", index=False)
    return likelihoods_dict


# function adapted from https://github.com/jdtoprug/EpistemicToMProject
def rfx_bms(name_likelihood_file="likelihoods", name_pred_file="predictions_tom", replace_all=False, verbose=False,
            converge_diff=0.001):
    """
    Run RFX-BMS on a model of Cheryl's Puzzle

    :param name_likelihood_file: the path to the likelihoods csv file
    :param name_pred_file: the path the predictions csv file
    :param verbose: if True, prints debug statements
    :param converge_diff: if, between iterations, each element in alpha has changed by this value or less, stop iterating
    """
    logdict = get_best_models_for_each_subj(name_likelihood_file=name_likelihood_file, name_pred_file=name_pred_file,
                                            replace_all=replace_all)
    likelihood_df = pd.read_csv(f"{name_likelihood_file}.csv")

    # Algorithm for RFX-BMS as detailed in 'Bayesian model selection for group studies' (Stephan et al., 2009)
    a0 = [1] * (len(set(likelihood_df["Model.idx"])))  # alpha_0, with one element for levels 0 through level maxtom, and an additional element for the random model
    a = a0.copy()  # We don't change a0
    # Until convergence:
    cont = True
    while (cont):
        prev = a.copy()  # Previous alpha
        sumdg = scipy.special.digamma(sum(a))  # Digamma of sum over k of alpha_k
        if verbose:
            print("a: " + str(a))
            print("sum(a): " + str(sum(a)))
            print("scipy.special.digamma(sum(a)) (sumdg): " + str(sumdg))
        listdg = []  # For each k, Psi(alpha_k) - Psi(sum over k of alpha_k)
        for k in range(len(a)):  # For each model
            if verbose:
                print("scipy.special.digamma(" + str(a[k]) + ") = " + str(scipy.special.digamma(a[k])))
            listdg.append(
                scipy.special.digamma(a[k]) - sumdg)  # Digamma of alpha_k - digamma of sum over k of alpha_k
        # Loop over models and subjects
        b = [0] * len(set(likelihood_df["Model.idx"]))  # For each k a beta_k
        if verbose:
            print("scipy.special.digamma(a[k]) - sumdg for each k: " + str(listdg))
            print("b before adding: " + str(b))
        for player in set(likelihood_df["Subject.id"]):  # Loop over all 211 players
            if verbose:
                print("player: " + str(player))
            sumunk = 0  # Sum over k of player's u_{nk}'s
            unklist = []
            for k in range(len(a)):  # Loop over models
                unk = math.exp(logdict[(player, k)] + listdg[k])  # Calculate u_{nk}
                if verbose:
                    print("model " + str(k))
                    print("listdg[k]: " + str(listdg[k]))
                    print("logdict[(player,k)]: " + str(logdict[(player, k)]))
                    print("unk: " + str(unk))
                unklist.append(unk)
                sumunk = sumunk + unk
            for k in range(len(a)):  # Loop over models again
                b[k] = b[k] + (unklist[k] / sumunk)  # Update b_k
            if verbose:
                print("unklist: " + str(unklist))
                print("sumunk: " + str(sumunk))
                print("new b: " + str(b))
        for k in range(len(a)):  # Update alpha
            a[k] = a0[k] + b[k]  # alpha = alpha_0 + beta
        if verbose:
            print("final b: " + str(b))
        cont = False

        # Check whether convergence has been achieved
        highestdiff = 0
        for k in range(len(a)):
            if abs(a[k] - prev[k]) > highestdiff:
                highestdiff = abs(a[k] - prev[k])
            if abs(a[k] - prev[k]) > converge_diff:
                cont = True
        if verbose:
            input("Press enter to continue")
            print("%\n\n\n@")
    # Normalize final alpha so elements sum to 1
    suma = 0
    for ak in a:
        suma += ak
    for k in range(len(a)):
        a[k] = a[k] / suma

    print("alpha after convergence:")
    names = [x for x in range(len(set(likelihood_df["Model.idx"]))-1)]
    names.append("random")
    print("level        estimated frequency")
    for i in range(len(a)):
        if i < len(a) - 1:
            print(str(names[i]) + "            " + str(a[i]))
        else:
            print(str(names[i]) + "       " + str(a[i]))
    print("String for copying into R:")
    print("<- c(" + str(a)[1:-1] + ")")



if __name__ == "__main__":
    rfx_bms(replace_all=True)
