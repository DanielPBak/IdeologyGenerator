#!/usr/bin/env python3
"""
Generate test fixtures for cross-language verification of the ideology generator.

This script:
1. Fetches the CSV from Google Sheets
2. Parses it using the Python Generator class (from lambda_function.py)
3. Records the parsed word lists so the JS test doesn't need network access
4. Records the interleaved sequence of random.random() and random.choice() calls
5. Generates ideologies and saves everything as test_fixtures.json

Run: .venv/bin/python3 test_generate_fixtures.py
Output: test_fixtures.json

Note: The Generator class in lambda_function.py uses class-level mutable attributes,
so all instances share the same word lists. The module-level code also fetches CSV
and calls get_words() on import. We work around this by clearing the class attributes
before our test run.
"""

import json
import random
import sys
import os

# Import Generator from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# lambda_function.py runs module-level code on import (fetches CSV, creates Generator).
from lambda_function import Generator, url
from urllib import request


def clear_generator_class_attrs():
    """Reset all class-level mutable attributes on Generator so a fresh instance starts clean."""
    Generator.desc_adjs = []
    Generator.desc_adjs_weights = []
    Generator.desc_adjs_hasp_weights = []
    Generator.desc_nouns = []
    Generator.desc_nouns_weights = []
    Generator.desc_nouns_hasp_weights = []
    Generator.prefixes = []
    Generator.prefix_weights = []
    Generator.prefix_hasp_weights = []
    Generator.nouns = []
    Generator.nouns_weights = []
    Generator.nouns_hasp_weights = []
    Generator.adverbs = []
    Generator.adverbs_weights = []
    Generator.endings = []
    Generator.endings_weights = []
    Generator.all_descs = []
    Generator.all_descs_weights = []
    Generator.all_descs_hasp_weights = []
    Generator.rows = []


def main():
    # Fetch the CSV ourselves (independent of the module-level fetch)
    print("Fetching CSV from Google Sheets...")
    response = request.urlopen(url)
    html = response.read()
    csv_text = html.decode('utf-8')

    # Clear class-level state from the module-level import, then parse fresh
    clear_generator_class_attrs()

    gen = Generator(html)
    gen.get_words()

    # Collect parsed word lists for comparison
    word_lists = {
        'desc_adjs': gen.desc_adjs,
        'desc_adjs_weights': gen.desc_adjs_weights,
        'desc_adjs_hasp_weights': gen.desc_adjs_hasp_weights,
        'desc_nouns': gen.desc_nouns,
        'desc_nouns_weights': gen.desc_nouns_weights,
        'desc_nouns_hasp_weights': gen.desc_nouns_hasp_weights,
        'prefixes': gen.prefixes,
        'prefix_weights': gen.prefix_weights,
        'prefix_hasp_weights': gen.prefix_hasp_weights,
        'nouns': gen.nouns,
        'nouns_weights': gen.nouns_weights,
        'nouns_hasp_weights': gen.nouns_hasp_weights,
        'adverbs': gen.adverbs,
        'adverbs_weights': gen.adverbs_weights,
        'endings': gen.endings,
        'endings_weights': gen.endings_weights,
        'all_descs': gen.all_descs,
        'all_descs_weights': gen.all_descs_weights,
        'all_descs_hasp_weights': gen.all_descs_hasp_weights,
    }

    # --- Test weighted_choice with known random values ---
    # Save and restore random.random around these tests since we temporarily patch it
    saved_random = random.random

    weights_test_cases = [
        [1, 1, 1],          # uniform
        [1, 2, 3],          # increasing
        [5, 1, 1],          # heavy first
        [0.5, 0.5, 2.0],   # mixed
    ]

    random_values_for_weighted = [0.0, 0.1, 0.25, 0.33, 0.5, 0.6, 0.75, 0.9, 0.99, 0.999]

    weighted_choice_results = []
    for weights in weights_test_cases:
        for rv in random_values_for_weighted:
            # Patch random.random to return our specific value for this test
            random.random = lambda rv=rv: rv
            result = gen.weighted_choice(weights)
            weighted_choice_results.append({
                'weights': weights,
                'random_value': rv,
                'expected_index': result,
            })

    # Restore random.random before proceeding
    random.random = saved_random

    # --- Record interleaved random calls during ideology generation ---
    # We record every call in order, tagged by type, so JS can replay them exactly.
    interleaved_calls = []

    random.seed(42)
    original_random = random.random
    original_choice = random.choice

    def recording_random():
        val = original_random()
        interleaved_calls.append({'type': 'random', 'value': val})
        return val

    def recording_choice(seq):
        result = original_choice(seq)
        seq_list = list(seq)
        idx = seq_list.index(result)
        interleaved_calls.append({'type': 'choice', 'index': idx, 'seq_len': len(seq_list)})
        return result

    random.random = recording_random
    random.choice = recording_choice

    # Clear and re-parse for a clean generation run
    clear_generator_class_attrs()
    gen2 = Generator(html)
    gen2.get_words()

    # Reset seed right before generation so the recording is clean
    random.seed(42)
    interleaved_calls.clear()

    n_ideologies = 50
    ideologies, traces = gen2.get_ideologies(n_ideologies)

    # Restore originals
    random.random = original_random
    random.choice = original_choice

    n_random = sum(1 for c in interleaved_calls if c['type'] == 'random')
    n_choice = sum(1 for c in interleaved_calls if c['type'] == 'choice')
    print(f"Generated {len(ideologies)} ideologies")
    print(f"Recorded {len(interleaved_calls)} total calls ({n_random} random, {n_choice} choice)")

    # Print first 10 for visual inspection
    for i, ideo in enumerate(ideologies[:10]):
        print(f"  {i}: {ideo}")

    # --- Build fixtures ---
    fixtures = {
        'csv_text': csv_text,
        'word_lists': word_lists,
        'weighted_choice_tests': weighted_choice_results,
        'generation': {
            'n_ideologies': n_ideologies,
            'interleaved_calls': interleaved_calls,
            'ideologies': ideologies,
            'traces': traces,
        },
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_fixtures.json')
    with open(output_path, 'w') as f:
        json.dump(fixtures, f, indent=2)

    print(f"\nFixtures written to {output_path}")
    print(f"File size: {os.path.getsize(output_path)} bytes")


if __name__ == '__main__':
    main()
