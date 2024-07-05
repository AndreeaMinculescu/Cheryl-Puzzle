# Credits: https://github.com/jdtoprug/EpistemicToMProject

import pandas as pd
from puzzle_formalism import Puzzle
from epistemic_model import EpistemicModel
import os
import math
import scipy
from utilities import plot_bar, plot_coherence

CONFIG = "cut_1_lrrl_2_lr_all" # identification string for plots with the same configuration
SAVE_BOOL = True
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

    :param name_predictions_file: path to file to save predictions in
    :param max_pa_tom_level: the maximum possible level of ToM for public announcements
    """
    # read in subject data
    subj_df = pd.read_csv("../analysis/All answers_puzzles.csv")
    # uncomment below to only process wrong answers; change to value 1 for only correct answers
    # subj_df = subj_df.loc[(subj_df["Is.correct"] == 1)]
    # uncomment and adjust below to only process certain levels of ToM
    # subj_df = subj_df.loc[(subj_df["Level"] == 4)]
    # read in question bank
    questions_df = pd.read_csv("../interface/question_bank.csv")
    # initialize prediction dataframe
    predictions_df = pd.DataFrame(columns=["Subject.id", "Trial", "ToM.level", "Correct.answer", "Subject.answer",
                                           "Is.subject.correct", "Model.predictions", "Is.model.correct"])
    # initialize puzzle object
    cb = Puzzle(list_players=["a", "b"], visibility=[[True, False], [False, True]])

    # for each data entry
    for idx, row in subj_df.iterrows():
        # get the correct answer to the current puzzle
        correct_answer = questions_df["Translated answer"].loc[questions_df["IDX"] == row["Index"]].values[0]

        model_predictions = {}
        model_is_correct = []
        model_cutting_dirs_config = ["lr", "rl"]

        # initialize epistemic model
        temp_solver = EpistemicModel(1, max_pa_tom_level, row["Level"] - 1, cb)
        # model_level is defined as the maximum level of ToM that the model can process; the model cuts off operators
        # in statements with higher ToM level than model_level, until the statement reaches model_level ToM
        # note: model_level = 0 means that cutting is disabled
        for model_level in range(max_pa_tom_level):
            for model_cutting_dir in model_cutting_dirs_config:
                # get the name of the current model configuration
                if model_level == 0:
                    model_name = "Epistemic"
                else:
                    model_name = f"Cut {model_level}-{model_cutting_dir}"

                # for epistemic model (model_level=0) compute answer only once (model_cutting_dir has no effect;
                # for cut-2 model (model_level=2), only cut from left or from right (both give the same answer)
                if model_level in [0, 2] and model_cutting_dir != model_cutting_dirs_config[0]:
                    continue
                # get the answer predicted by the model
                model_answer = get_prediction_one_model(temp_solver, {"model_level": model_level,
                                                                      "cutting_direction": model_cutting_dir})
                # store the prediction
                model_predictions[model_name] = model_answer
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


def count_all_answers(all_part_answers_list, plot_population_distrib=False):
    """
    Compute and plot the frequency of answers within the sample of participants.
    
    :param all_part_answers_list: list of all answers given by all participants
    :param plot_population_distrib: if True, then plot the frequency of answers
    :return: a dict, where the keys are unique answers and the values are the number of occurrences per unique answer
    """
    # compute frequency of each unique answer
    all_subj_answer_dict = {}
    for ans in all_part_answers_list:
        try:
            all_subj_answer_dict[ans] += 1
        except KeyError:
            all_subj_answer_dict[ans] = 1

    # optionally, plot the frequency of answers
    if plot_population_distrib:
        all_subj_answer_dict = dict(sorted(all_subj_answer_dict.items(), key=lambda item: item[1], reverse=True))
        plot_bar(all_subj_answer_dict, f"Frequency of answers aggregated\nover all participants and puzzles",
                 "Answer", "Frequency of answer", (0, max(all_subj_answer_dict.values())),
                 (0, len(all_subj_answer_dict)),
                 "plots/paper/freq_all_answers")

    return all_subj_answer_dict


def compute_likelihood(correct, incorrect, penalty=1/12):
    """
    Calculate log-likelihood as correct * ln(1 - e) + incorrect * ln(e * penalty)

    Function adapted from https://github.com/jdtoprug/EpistemicToMProject

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


def compute_error_likelihood_random(subj_answer_dict, population_answer_dict):
    """
    Calculates likelihood for random model, taking into account the answer distribution of all participants.

    Function adapted from https://github.com/jdtoprug/EpistemicToMProject

    :param subj_answer_dict: dictionary where the keys are unique answers given by the participant and the values are
    the number of occurrences
    :poaram population_answer_dict: dictionary where the keys are unique answers given by all participants and the
    values are the number of occurrences
    :return: log-likelihood of random model corresponding to participant
    """
    likelihood = 0
    for ans in subj_answer_dict.keys():
        likelihood += subj_answer_dict[ans] * math.log(population_answer_dict[ans]/sum(population_answer_dict.values()))
    return likelihood


def compute_correct_rate_random(subj_answer_dict, population_answer_dict):
    """
    Calculates coherence for random model, taking into account the answer distribution of all participants

    :param subj_answer_dict: dictionary where the keys are unique answers given by the participant and the values are
    the number of occurrences
    :param population_answer_dict: dictionary where the keys are unique answers given by all participants and the
    values are the number of occurrences
    :return: proportion of times random model corresponds to participant
    """
    rate = 0
    for ans in subj_answer_dict.keys():
        rate += subj_answer_dict[ans] * (population_answer_dict[ans]/sum(population_answer_dict.values()))
    return rate/sum(subj_answer_dict.values())


def generate_log_likelihoods(name_likelihood_file="likelihoods", name_pred_file="predictions_tom", replace_all=False):
    """
    Computes evidence for each model and saves to file

    :param name_likelihood_file: file path where log-likelihoods for each model will be saved
    :param name_pred_file: file path where all model predictions for participants' answers have been/will be saved
    :param replace_all: if True, then the model predictions are computed from scratch; if False, then the model
    predictions are read in from file
    """
    # if the predictions file does not exist or replace_all is True, then first generate it
    if not os.path.exists(f"{name_pred_file}.csv") or replace_all:
        generate_all_predictions(name_predictions_file=name_pred_file)
    # load the prediction file
    prediction_model_df = pd.read_csv(f"{name_pred_file}.csv")

    # initialize dataframe for model evidence
    likelihood_df = pd.DataFrame(columns=["Subject.id", "Model.name", "Log-likelihood", "Correct.rate",
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
        all_models_answers = [list(eval(x).values()) for x in prediction_model_df["Model.predictions"].loc[
            prediction_model_df["Subject.id"] == subj_id].values]
        # retrieve which answers were correct and which incorrect for all models
        all_models_bool_answers = [eval(x) for x in prediction_model_df["Is.model.correct"].loc[
            prediction_model_df["Subject.id"] == subj_id].values]
        # iterate through all ToM models
        for model_idx, model_name in enumerate(eval(prediction_model_df["Model.predictions"][0])):
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
            likelihood_df.loc[likelihood_df.shape[0]] = [subj_id, model_name, likelihood,
                                                         number_same_answer/len(model_answers), subj_accuracy_score,
                                                         model_accuracy_score]

        # count the number of occurrences for each unique answer for the current participant
        dict_count_subj_answers = count_subject_answers(subj_answers)
        dict_count_all_answers = count_all_answers(list(prediction_model_df["Subject.answer"]))
        # compute the log-likelihood that the current participants used random model's strategy, given the distribution
        # of answers for that participant
        likelihood_random = compute_error_likelihood_random(dict_count_subj_answers, dict_count_all_answers)
        # compute the coherence of the random model
        coherence_random = compute_correct_rate_random(dict_count_subj_answers, dict_count_all_answers)

        # store data
        likelihood_df.loc[likelihood_df.shape[0]] = [subj_id, "Random", likelihood_random, coherence_random,
                                                     subj_accuracy_score, ""]

    likelihood_df.reset_index(drop=True, inplace=True)
    likelihood_df.to_csv(f"{name_likelihood_file}.csv", index=False)


################## RFX-BMS ##################


def get_best_models_for_each_subj(name_likelihood_file="likelihoods", name_pred_file="predictions_tom",
                                  name_correct_rates_file="correct_rates", replace_all=False):
    """
    For each participant, find the model with the best correct rate.

    Function adapted from https://github.com/jdtoprug/EpistemicToMProject

    :param name_likelihood_file: the path to the likelihoods csv file
    :param name_pred_file: the path to the predictions csv file
    :param name_correct_rates_file: file path where correct rates will be saved
    :param replace_all: if True, then the model predictions are computed from scratch; if False, then read in from file
    :return: a dict storing the likelihoods for each subject-model pair
    """
    # if log-likelihood file does not exist or replace_all is set to True, then first generate it
    if not os.path.exists(f"{name_likelihood_file}.csv") or replace_all:
        generate_log_likelihoods(name_likelihood_file=name_likelihood_file, name_pred_file=name_pred_file,
                                 replace_all=replace_all)
    pred_df = pd.read_csv(f"{name_pred_file}.csv")
    likelihood_df = pd.read_csv(f"{name_likelihood_file}.csv")

    likelihoods_dict = {}
    correct_rates_dict = {}
    correct_rates_df = pd.DataFrame(columns=list(set(pred_df["Subject.id"])))
    correct_rates_df = correct_rates_df.append(pd.Series(), ignore_index=True)
    correct_rates_df = correct_rates_df.append(pd.Series(), ignore_index=True)
    # extract relevant information from the likelihood dataframe
    for idx, row in likelihood_df.iterrows():
        likelihoods_dict[(row[0], row[1])] = row[2]
        correct_rates_dict[(row[0], row[1])] = row[3]

    all_best_correct_rates = []
    best_correct_rates_per_model = {model_name: [] for model_name in set(likelihood_df["Model.name"])}
    number_choices_best_per_model = {model_name: 0 for model_name in set(likelihood_df["Model.name"])}
    # get and store the model(s) with the best correct rate for each participant
    for subj_idx, subj in enumerate(set(likelihood_df["Subject.id"])):
        best_correct_rate = 0
        best_models = []

        for model_id in set(likelihood_df["Model.name"]):
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

        correct_rates_df[subj][0] = best_models
        correct_rates_df[subj][1] = best_correct_rate

    correct_rates_df.to_csv(f"{name_correct_rates_file}.csv", index=False)
    return likelihoods_dict


def rfx_bms(name_likelihood_file="likelihoods", name_pred_file="predictions_tom",
            name_correct_rates_file="correct_rates", replace_all=False, verbose=False, converge_diff=0.001):
    """
    Run RFX-BMS on a model of Cheryl's Puzzle.

    Function adapted from https://github.com/jdtoprug/EpistemicToMProject

    :param name_likelihood_file: the path to the likelihoods csv file
    :param name_pred_file: the path the predictions csv file
    :param name_correct_rates_file: the path to the correct rates csv file
    :param replace_all: if True, then the model predictions are computed from scratch; if False, then read in from file
    :param verbose: if True, prints debug statements
    :param converge_diff: if, between iterations, each element in alpha has changed by this value or less,
    stop iterating
    """
    logdict = get_best_models_for_each_subj(name_likelihood_file=name_likelihood_file, name_pred_file=name_pred_file,
                                            name_correct_rates_file=name_correct_rates_file, replace_all=replace_all)
    likelihood_df = pd.read_csv(f"{name_likelihood_file}.csv")

    # Algorithm for RFX-BMS as detailed in 'Bayesian model selection for group studies' (Stephan et al., 2009)
    a0 = {model_name: 1 for model_name in (set(likelihood_df["Model.name"]))}  # alpha_0, with one element for levels 0 through level maxtom, and an additional element for the random model
    a = a0.copy()  # We don't change a0
    # Until convergence:
    cont = True
    while (cont):
        prev = a.copy()  # Previous alpha
        sumdg = scipy.special.digamma(sum(a.values()))  # Digamma of sum over k of alpha_k
        if verbose:
            print("a: " + str(a))
            print("sum(a): " + str(sum(a.values())))
            print("scipy.special.digamma(sum(a)) (sumdg): " + str(sumdg))
        listdg = []  # For each k, Psi(alpha_k) - Psi(sum over k of alpha_k)
        for model_name in a.keys():  # For each model
            if verbose:
                print("scipy.special.digamma(" + str(a[model_name]) + ") = " + str(scipy.special.digamma(a[k])))
            listdg.append(
                scipy.special.digamma(a[model_name]) - sumdg)  # Digamma of alpha_k - digamma of sum over k of alpha_k
        # Loop over models and subjects
        b = [0] * len(set(likelihood_df["Model.name"]))  # For each k a beta_k
        if verbose:
            print("scipy.special.digamma(a[k]) - sumdg for each k: " + str(listdg))
            print("b before adding: " + str(b))
        for player in set(likelihood_df["Subject.id"]):  # Loop over all 211 players
            if verbose:
                print("player: " + str(player))
            sumunk = 0  # Sum over k of player's u_{nk}'s
            unklist = []
            for k, model_name in enumerate(list(a.keys())):  # Loop over models
                unk = math.exp(logdict[(player, model_name)] + listdg[k])  # Calculate u_{nk}
                if verbose:
                    print("model " + str(model_name))
                    print("listdg[k]: " + str(listdg[k]))
                    print("logdict[(player,k)]: " + str(logdict[(player, model_name)]))
                    print("unk: " + str(unk))
                unklist.append(unk)
                sumunk = sumunk + unk
            for k in range(len(a)):  # Loop over models again
                b[k] = b[k] + (unklist[k] / sumunk)  # Update b_k
            if verbose:
                print("unklist: " + str(unklist))
                print("sumunk: " + str(sumunk))
                print("new b: " + str(b))
        for k, model_name in enumerate(list(a.keys())):  # Update alpha
            a[model_name] = a0[model_name] + b[k]  # alpha = alpha_0 + beta
        if verbose:
            print("final b: " + str(b))
        cont = False

        # Check whether convergence has been achieved
        highestdiff = 0
        for model_name in a.keys():
            if abs(a[model_name] - prev[model_name]) > highestdiff:
                highestdiff = abs(a[model_name] - prev[model_name])
            if abs(a[model_name] - prev[model_name]) > converge_diff:
                cont = True
        if verbose:
            input("Press enter to continue")
            print("%\n\n\n@")
    # Normalize final alpha so elements sum to 1
    suma = 0
    for ak in a.values():
        suma += ak
    for model_name in a.keys():
        a[model_name] = round(a[model_name] / suma, 3)

    print("alpha after convergence:")
    a = dict(sorted(a.items()))
    print("model" + 10*" " + "estimated frequency")
    for idx, model_name in enumerate(list(a.keys())):
        print(str(model_name) + (10 - abs(len("model") - len(model_name))) * " " + str(a[model_name]))

    # if SAVE_BOOL set to True, then plot RFX-BMS results and coherence plots
    if SAVE_BOOL:
        plot_bar(a, "Proportion of fit for each strategy", "Model", "Proportion of population", (0, 0.8), (0, len(a)),
                 f"plots/propfit_{CONFIG}", rotation_x=45)
        plot_coherence(name_correct_rates_file, max(a, key=a.get), f"plots/distribcoh_{CONFIG}")


if __name__ == "__main__":
    rfx_bms(replace_all=True)
