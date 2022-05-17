import pytest
import numpy as np

import tensorflow_decision_forests as tfdf
from dtreeviz.models.tfdf_decision_tree import ShadowTFDFTree


@pytest.fixture()
def features_clf():
    return ["Pclass", "Sex_label", "Embarked_label", "Age_mean", "SibSp", "Parch", "Fare"]


@pytest.fixture()
def tfdf_rf_model(dataset_spark_tf):
    """
    The saved model is not the same with the raw one. When we load it, it is an instance of a _RandomForestInspector class
    Because of this, it would be better to recreate the same model and to be used in these unit tests.
    """

    random_state = 1234
    target_clf = "Survived"
    train_clf = tfdf.keras.pd_dataframe_to_tf_dataset(dataset_spark_tf, label=target_clf)
    model_clf = tfdf.keras.RandomForestModel(max_depth=3, random_seed=random_state)
    model_clf.fit(train_clf)

    return model_clf


@pytest.fixture()
def tfdf_shadow_clf(tfdf_rf_model, dataset_spark_tf, features_clf):
    target_clf = "Survived"

    tfdf_shadow = ShadowTFDFTree(tfdf_rf_model,
                                 tree_index=0,
                                 x_data=dataset_spark_tf[features_clf],
                                 y_data=dataset_spark_tf[target_clf],
                                 feature_names=features_clf,
                                 target_name=target_clf,
                                 class_names=[0, 1])

    return tfdf_shadow


def test_is_fit(tfdf_shadow_clf):
    assert tfdf_shadow_clf.is_fit() is True


def test_get_children_left(tfdf_shadow_clf):
    assert tfdf_shadow_clf.get_children_left() == {0: 1, 1: 2, 4: 5, 2: -1, 3: -1, 5: -1, 6: -1}


def test_get_children_right(tfdf_shadow_clf):
    assert tfdf_shadow_clf.get_children_right() == {1: 3, 0: 4, 4: 6, 2: -1, 3: -1, 5: -1, 6: -1}


def test_nclasses(tfdf_shadow_clf):
    assert tfdf_shadow_clf.nclasses() == 2


def test_classes(tfdf_shadow_clf):
    assert (tfdf_shadow_clf.classes() == [0, 1]).all()


def test_get_features(tfdf_shadow_clf):
    assert (tfdf_shadow_clf.get_features() == [1,  0, -2, -2,  5, -2, -2]).all()


def test_get_node_feature(tfdf_shadow_clf):
    assert tfdf_shadow_clf.get_node_feature(0) == 1
    assert tfdf_shadow_clf.get_node_feature(4) == 5
    assert tfdf_shadow_clf.get_node_feature(2) == -2


def test_get_thresholds(tfdf_shadow_clf):
    assert (tfdf_shadow_clf.get_thresholds() == [0.5, 1.5, -2.0, -2.0, 2.5, -2.0, -2.0]).all()


def test_get_node_samples(tfdf_shadow_clf):
    assert len(tfdf_shadow_clf.get_node_samples()[0]) == 891, "Node samples for node 0 should be 891"
    assert len(tfdf_shadow_clf.get_node_samples()[1]) == 577, "Node samples for node 1 should be 577"
    assert len(tfdf_shadow_clf.get_node_samples()[2]) == 122, "Node samples for node 2 should be 122"
    assert len(tfdf_shadow_clf.get_node_samples()[4]) == 314, "Node samples for node 4 should be 314"


def test_get_node_nsamples(tfdf_shadow_clf):
    assert tfdf_shadow_clf.get_node_nsamples(0) == 891
    assert tfdf_shadow_clf.get_node_nsamples(1) == 577
    assert tfdf_shadow_clf.get_node_nsamples(2) == 122
    assert tfdf_shadow_clf.get_node_nsamples(4) == 314


def test_get_node_nsamples_by_class(tfdf_shadow_clf):
    assert tfdf_shadow_clf.get_node_nsamples_by_class(0) == (549, 342)
    assert tfdf_shadow_clf.get_node_nsamples_by_class(1) == (468, 109)
    assert tfdf_shadow_clf.get_node_nsamples_by_class(4) == (81, 233)


def test_get_prediction(tfdf_shadow_clf):
    assert tfdf_shadow_clf.get_prediction(0) == 0
    assert tfdf_shadow_clf.get_prediction(1) == 0
    assert tfdf_shadow_clf.get_prediction(2) == 0
    assert tfdf_shadow_clf.get_prediction(3) == 0
    assert tfdf_shadow_clf.get_prediction(4) == 1
    assert tfdf_shadow_clf.get_prediction(5) == 1
    assert tfdf_shadow_clf.get_prediction(6) == 0


def test_get_max_depth(tfdf_shadow_clf):
    assert tfdf_shadow_clf.get_max_depth() == 3


def test_is_categorical_split(tfdf_shadow_clf):
    assert tfdf_shadow_clf.is_categorical_split(0) is False
    assert tfdf_shadow_clf.is_categorical_split(1) is False








