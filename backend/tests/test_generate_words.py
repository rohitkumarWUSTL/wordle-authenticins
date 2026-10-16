"""Tests for the plural filter used when building the answer pool."""

from __future__ import annotations

from scripts.generate_words import _is_plural


def test_regular_s_plural():
    source = {"crane", "cranes", "slate"}
    assert _is_plural("cranes", source) is True


def test_es_plural():
    source = {"box", "boxes", "fox"}
    assert _is_plural("boxes", source) is True


def test_ies_plural():
    source = {"fly", "flies", "sky"}
    assert _is_plural("flies", source) is True


def test_ves_plural_f():
    source = {"wife", "wives", "knife"}
    assert _is_plural("wives", source) is True


def test_ves_plural_fe():
    source = {"knife", "knives", "life"}
    assert _is_plural("knives", source) is True


def test_singular_is_not_plural():
    source = {"crane", "cranes", "slate"}
    assert _is_plural("crane", source) is False


def test_word_ending_in_s_without_singular_is_not_plural():
    source = {"basis", "chaos", "atlas"}
    assert _is_plural("basis", source) is False
    assert _is_plural("chaos", source) is False
    assert _is_plural("atlas", source) is False


def test_plural_without_singular_in_source_is_not_plural():
    # "cranes" is a plural, but if "crane" isn't in the source we can't
    # tell, so we don't flag it.
    source = {"cranes", "slate"}
    assert _is_plural("cranes", source) is False


def test_plural_with_short_singular_is_plural():
    # "frog" is 4 letters and wouldn't be in the length-filtered source,
    # but it's in the full word list, so "frogs" should still be flagged.
    all_words = {"frog", "frogs", "crane", "cranes"}
    assert _is_plural("frogs", all_words) is True


def test_es_plural_with_short_singular_is_plural():
    all_words = {"box", "boxes", "crane", "cranes"}
    assert _is_plural("boxes", all_words) is True
