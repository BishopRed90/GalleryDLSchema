from dataclasses import dataclass
from typing import Annotated

from pydantic import BaseModel, Field
from textwrap import dedent
import json
import pathlib

from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue


@dataclass
class Filename:
    string: str = Field(
        title="String",
        description="A format string to build filenames for downloaded files with.",
        examples=["{category}/{subcategory}/{image-id}.{extension}"],
    )

    obj: dict = Field(
        title="Object",
        description=dedent(
            """Must contain Python expressions mapping to the filename format strings to use.
            These expressions are evaluated in the order as specified in Python 3.6+ and in an undetermined 
            order
            in Python 3.4 and 3.5."""),
        examples=[
            {
                "extension == 'mp4'": "{id}_video.{extension}",
                "'nature' in title": "{id}_{title}.{extension}",
                "": "{id}_default.{extension}"
            }
        ]
    )

    definition = Field(
        description=dedent("""
            The available replacement keys depend on the extractor used. 
            A list of keys for a specific one can be acquired by calling gallery-dl with the ```-K/--list-keywords``` 
            command-line option.
            
            ```markdown 
            $ gallery-dl -K https://seiga.nicovideo.jp/seiga/im5977527
            Keywords for directory names:
            ----------------
            category
              seiga
            subcategory
              image
            
            Keywords for filenames:
            -----------------------
            category
              seiga
            extension
              None
            image-id
              5977527
            subcategory
              image ```
        """),
        title="Filename - Format Strings",
    )


@dataclass
class BaseDirectory:
    string: str = Field(
        title="String",
        description="A format string to build directory names for downloaded files with.",
        examples=["$HOME/Downloads", "~/path/to/download", f"C:\\Users\\User\\Downloads"],
    )

    array: list[str] = Field(
        title="List of Strings",
        description=dedent("A list with each part of the path as a separate string."),
        examples=[["$HOME", "Downloads", "Location"]]
    )

    definition: Field = Field(
        alias="base-directory",
        default="./gallery-dl/",
        description=dedent(f"""
            Directory path used as base for all download destinations. A Path is a ``string`` representing the 
            location of a file or directory.
    
            Simple [tilde expansion](https://docs.python.org/3/library/os.path.html#os.path.expanduser) and [
            environment variable expansion](
            https://docs.python.org/3/library/os.path.html#os.path.expandvars) is supported.
    
            In Windows environments, backslashes (``"\\"``) can, in addition to forward slashes (``"/"``), 
            be used as path separators. Because backslashes are JSON's 
            escape character, they themselves have to be escaped. 
            The path ``C:\\path\\to\\file.ext`` has therefore to be written as ``"C:\\\\path\\\\to\\\\file.ext"`` if 
            you want to use backslashes.
                   """)
    )


@dataclass
class Directory:
    array: list[str] = Field(
        json_schema_extra={"additionalItems": True},
        title="List of Strings",
        description=dedent("A list with each part of the path as a separate string."),
        examples=[["Manga", "{category}", "{manga}", "c{chapter} - {title}"]]
    )

    obj: dict = Field(
        title="Object",
        description=dedent(
            """Must contain Python expressions mapping to the filename format strings to use.
            These expressions are evaluated in the order as specified in Python 3.6+ and in an undetermined 
            order
            in Python 3.4 and 3.5."""),
        examples=[
            {
                "'nature' in content": ["Nature Pictures"],
                "retweet_id != 0": ["{category}", "{user[name]}", "Retweets"],
                "": ["{category}", "{user[name]}"]
            }
        ]
    )

    definition: Field = Field(
        description=dedent(f"""
                A list of format strings to build target directory paths with.

                If this is an object, it must contain Python expressions mapping to the list of format strings to use.

                Each individual string in such a list represents a single path segment, which will be joined together 
                and appended to the base-directory 
                to form the complete target directory path.
                   """)
    )


class Extractor(BaseModel):
    """
Each extractor is identified by its ``category`` and ``subcategory``. The ``category`` is the lowercase site name
without any spaces or special characters, which is usually just the module name (``pixiv``, ``danbooru``,...).
The ``subcategory`` is a lowercase word describing the general functionality of that extractor (``user``,
``favorite``, ``manga``, ...).

Each one of the following options can be specified on multiple levels of the configuration tree:

================== =======
Base level:        ``extractor.<option-name>``
Category level:    ``extractor.<category>.<option-name>``
Subcategory level: ``extractor.<category>.<subcategory>.<option-name>``
================== =======

A value in a "deeper" level hereby overrides a value of the same name on a lower level. Setting the
``extractor.pixiv.filename`` value, for example, lets you specify a general filename pattern for all the
different pixiv extractors. Using the ``extractor.pixiv.user.filename`` value lets you override this general
pattern specifically for ``PixivUserExtractor`` instances.

The ``category`` and ``subcategory`` of all extractors are included in the output of ``gallery-dl
--list-extractors``.
For a specific URL these values can also be determined by using the ``-K``/``--list-keywords``
command-line option (see the example below).
    """

    class Config:
        populate_by_name = True

        json_schema_extra = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://example.com/schemas/Extractors/CommonExtractor.json"
        }
        extra = "forbid"  # Forbid extra inputs

    base_directory: Annotated[str, BaseDirectory.string] | Annotated[
        list[str], BaseDirectory.array] = BaseDirectory.definition
    filename: Annotated[str, Filename.string] | Annotated[dict, Filename.obj] = Filename.definition
    directory: Annotated[list[str], Directory.array] | Annotated[object, Directory.obj] = Directory.definition
    # parent_directory = None
    # parent_metadata = None
    # parent_skip = None
    # path_restrict = None
    #


class MyGenerateJsonSchema(GenerateJsonSchema):
    def sort(
            self, value: JsonSchemaValue, parent_key: str | None = None
    ) -> JsonSchemaValue:
        """No-op, we don't want to sort schema values at all."""
        return value


def export_json_schema(filename: str = "CommonExtractor.json", path: str | list[str] = "Extractors"):
    _file = pathlib.Path(path) / filename
    print(f"Exporting JSON Schema to {_file}...")
    with open(_file, 'w') as f:
        json.dump(Extractor.model_json_schema(schema_generator=MyGenerateJsonSchema),
                  f, indent=4, sort_keys=False)


def validate_extractor(schema: dict):
    extractor = Extractor(**schema)
    return extractor


def main():
    schema = {
        "extractor": {
            "base-directory": "./gallery-dl/",
            "filename": "Test/Path/{image-id}.{extension}"
        }
    }
    # extractor = validate_extractor(schema['extractor'])
    # print(extractor.model_dump_json(indent=4))
    # print(json.dumps(extractor.model_json_schema(), indent=4))


if __name__ == "__main__":
    main()
