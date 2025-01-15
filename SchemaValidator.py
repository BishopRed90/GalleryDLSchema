import json

from jsonschema import validate
from referencing import Registry, Resource
from json_schema_for_humans.generate import generate_from_filename
from json_schema_for_humans.generation_configuration import GenerationConfiguration
import PyDantic as pd

test_dict = {
    "extractor": {
        "filename": "Test.name",
        "directory": ["Test", "Path", "File"],
        "base-directory": "TEST/PATH/FILE",
    }
}


def load_schema(schema_file):
    with open(schema_file, 'r') as f:
        try:
            schema = Resource.from_contents(json.load(f))
            print("Schema loaded successfully")
        except json.JSONDecodeError:
            print("Invalid JSON")
    return schema


def validate_schema(schema: dict, data: dict, registry: Registry = None):
    try:
        validate(instance=data, schema=schema, registry=registry)
        print("Schema validated successfully")
    except Exception as e:
        print(f"Schema validation failed: {e}")


def main():
    pd.export_json_schema()
    markdown_options = {
        "fenced-code-blocks": {
            "cssclass": "highlight jumbotron"
        },
        "tables": None,
        "break-on-newline": True
    }
    md_config = GenerationConfiguration(copy_css=False, expand_buttons=True, template_name="md",
                                        markdown_options=markdown_options)
    js_config = GenerationConfiguration(expand_buttons=True, template_name="js_offline", collapse_long_examples=False,
                                        collapse_long_descriptions=False, copy_js=True,
                                        show_breadcrumbs=False, with_footer=False,
                                        custom_template_path="../GalleryDLSchema/Documentation/json_human/Templates/js_offline_custom/base.html",
                                        )
    generate_from_filename("GalleryDL_Main.json",
                           "../GalleryDLSchema/Documentation/json_human/output/GallerySchema_MD.html",
                           config=md_config)
    generate_from_filename("GalleryDL_Main.json",
                           "../GalleryDLSchema/Documentation/json_human/output/GallerySchema_JS.html", config=js_config)

    # gallery_schema = load_schema("GalleryDL_Main.json")
    # common_extractor = load_schema("Extractors/CommonTest.json")
    # custom_types = load_schema("CustomTypes.json")
    #
    # registry = Registry().with_resource(uri="gallerydl", resource=gallery_schema)
    # registry = registry.with_resource(uri="Extractors/CommonExtractor.json", resource=common_extractor)
    # registry = registry.with_resource(uri="CustomTypes.json", resource=custom_types)
    # # validate_schema(registry.contents("gallerydl"), test_dict, registry)


if __name__ == "__main__":
    main()
