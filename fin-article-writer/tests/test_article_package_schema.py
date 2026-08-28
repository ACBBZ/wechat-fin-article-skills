import json
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[1] / 'references' / 'article-package.schema.json'


def load_schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding='utf-8'))


def test_schema_requires_v3_style_and_semantic_anchors():
    schema = load_schema()
    required = set(schema['required'])
    assert 'style' in required
    assert 'section_anchors' in required

    anchors = schema['properties']['section_anchors']
    assert anchors['minItems'] == 3
    assert {'id', 'purpose'} <= set(anchors['items']['required'])


def test_schema_enforces_3000_to_3600_visible_chars():
    schema = load_schema()
    article = schema['properties']['article']
    assert 'visible_char_count' in article['required']
    visible = article['properties']['visible_char_count']
    assert visible['minimum'] == 3000
    assert visible['maximum'] == 3600


def test_schema_requires_three_auto_insert_images_with_anchor_ids():
    schema = load_schema()
    images = schema['properties']['images']
    assert images['minItems'] == 3
    assert images['minContains'] == 3
    assert 'anchor_id' in images['items']['properties']
    assert 'anchor_id' in images['contains']['required']

    roles = set(images['items']['properties']['role']['enum'])
    assert 'mechanism_explainer' in roles
    assert 'explanatory_visual' in roles


def test_schema_requires_v31_source_first_image_strategy():
    schema = load_schema()
    assert 'image_strategy' in schema['required']

    strategy = schema['properties']['image_strategy']
    required = set(strategy['required'])
    assert {
        'mode',
        'target_source_ratio',
        'source_visual_search_exhausted',
        'source_visual_inventory',
        'source_visual_count',
        'ai_fallback_used',
    } <= required
    assert strategy['properties']['mode']['const'] == 'source_first'
    assert strategy['properties']['target_source_ratio']['minimum'] == 0.67

    inventory = strategy['properties']['source_visual_inventory']
    assert inventory['type'] == 'array'
    assert {'source_id', 'source_title', 'source_url', 'inspected', 'usable_visuals'} <= set(
        inventory['items']['required']
    )


def test_schema_tracks_image_origin_and_ai_fallback_evidence():
    schema = load_schema()
    image_item = schema['properties']['images']['items']
    props = image_item['properties']

    assert 'origin_kind' in image_item['required']
    assert set(props['origin_kind']['enum']) == {
        'source_capture',
        'source_asset',
        'source_derived_chart',
        'ai_fallback',
    }
    assert 'source_id' in props
    assert 'source_locator' in props
    assert 'ai_fallback_reason' in props

    conditionals = image_item['allOf']
    assert any('source_id' in rule.get('then', {}).get('required', []) for rule in conditionals)
    assert any('ai_fallback_reason' in rule.get('then', {}).get('required', []) for rule in conditionals)


def test_ai_fallback_requires_exhausted_source_search():
    schema = load_schema()
    strategy = schema['properties']['image_strategy']
    fallback_rule = strategy['allOf'][0]

    assert fallback_rule['if']['properties']['ai_fallback_used']['const'] is True
    assert fallback_rule['then']['properties']['source_visual_search_exhausted']['const'] is True
    assert 'ai_fallback_reason' in fallback_rule['then']['required']


def test_cover_schema_carries_style_reference():
    schema = load_schema()
    cover = schema['properties']['cover']
    assert 'style_reference' in cover['required']
    style_reference = cover['properties']['style_reference']
    assert style_reference['type'] == 'object'
