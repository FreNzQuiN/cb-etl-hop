import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gen_pipelines_lib import (
    NAMA_BULAN,
    NAMA_HARI,
    csv_field,
    head,
    out_field,
    pipeline,
    script_transform,
    sel_field,
    tail,
    text_field,
    tulis,
)


def csv_input(nama, path, separator, fields, x, y, deskripsi=""):
    baris = head(nama, "CSVInput", x, y, deskripsi)
    baris += [
        "    <filename>%s</filename>" % path,
        "    <filename_field/>",
        "    <rownum_field/>",
        "    <include_filename>N</include_filename>",
        "    <separator>%s</separator>" % separator,
        "    <enclosure>&quot;</enclosure>",
        "    <header>Y</header>",
        "    <buffer_size>50000</buffer_size>",
        "    <lazy_conversion>N</lazy_conversion>",
        "    <add_filename_result>N</add_filename_result>",
        "    <parallel>N</parallel>",
        "    <newline_possible>N</newline_possible>",
        "    <encoding>UTF-8</encoding>",
        "    <fields>",
    ]
    for f in fields:
        baris += f
    baris += ["    </fields>"]
    baris += tail(x, y)
    return baris


def excel_input(nama, path, sheet, fields, x, y, deskripsi=""):
    baris = head(nama, "ExcelInput", x, y, deskripsi)
    baris += [
        "    <accept_filenames>N</accept_filenames>",
        "    <add_to_result_filenames>N</add_to_result_filenames>",
        "    <bad_line_files_extension>warning</bad_line_files_extension>",
        "    <error_ignored>N</error_ignored>",
        "    <error_line_files_extension>error</error_line_files_extension>",
        "    <error_line_skipped>N</error_line_skipped>",
        "    <fields>",
    ]
    for f in fields:
        baris += f
    baris += [
        "    </fields>",
        "    <file>",
        "      <file_required>N</file_required>",
        "      <filemask>%s</filemask>" % path,
        "      <include_subfolders>N</include_subfolders>",
        "      <name>%s</name>" % path,
        "    </file>",
        "    <header>Y</header>",
        "    <ignore_fields>N</ignore_fields>",
        "    <limit>0</limit>",
        "    <line_number_files_extension>line</line_number_files_extension>",
        "    <noempty>Y</noempty>",
        "    <sheetrownumfield>sheet_row</sheetrownumfield>",
        "    <sheets>",
        "      <sheet>",
        "        <name>%s</name>" % sheet,
        "        <startrow>0</startrow>",
        "        <startcol>0</startcol>",
        "        <is_regex>N</is_regex>",
        "      </sheet>",
        "    </sheets>",
        "    <shortFileFieldName>short_filename</shortFileFieldName>",
        "    <spreadsheet_type>SAX_POI</spreadsheet_type>",
        "    <stoponempty>N</stoponempty>",
        "    <strict_types>N</strict_types>",
    ]
    baris += tail(x, y)
    return baris


def table_input(nama, connection, sql, x, y, deskripsi=""):
    baris = head(nama, "TableInput", x, y, deskripsi)
    baris += [
        "    <connection>%s</connection>" % connection,
        "    <sql>%s</sql>" % sql,
        "    <limit>0</limit>",
        "    <lookup/>",
        "    <execute_each_row>N</execute_each_row>",
        "    <variables_active>N</variables_active>",
    ]
    baris += tail(x, y)
    return baris


def table_output(nama, connection, table, x, y, deskripsi=""):
    baris = head(nama, "TableOutput", x, y, deskripsi)
    baris += [
        "    <commit>500</commit>",
        "    <connection>%s</connection>" % connection,
        "    <fields>",
        "    </fields>",
        "    <ignore_errors>N</ignore_errors>",
        "    <partitioning_daily>N</partitioning_daily>",
        "    <partitioning_enabled>N</partitioning_enabled>",
        "    <partitioning_monthly>N</partitioning_monthly>",
        "    <return_keys>N</return_keys>",
        "    <specify_fields>N</specify_fields>",
        "    <table>%s</table>" % table,
        "    <tablename_in_field>N</tablename_in_field>",
        "    <tablename_in_table>Y</tablename_in_table>",
        "    <truncate>N</truncate>",
        "    <use_batch>N</use_batch>",
    ]
    baris += tail(x, y)
    return baris


def text_output(nama, path, fields, x, y, deskripsi=""):
    baris = head(nama, "TextFileOutput", x, y, deskripsi)
    baris += [
        "    <separator>,</separator>",
        "    <enclosure>&quot;</enclosure>",
        "    <enclosure_forced>N</enclosure_forced>",
        "    <enclosure_fix_disabled>N</enclosure_fix_disabled>",
        "    <header>Y</header>",
        "    <footer>N</footer>",
        "    <format>DOS</format>",
        "    <compression>None</compression>",
        "    <encoding>UTF-8</encoding>",
        "    <endedLine/>",
        "    <fileNameInField>N</fileNameInField>",
        "    <fileNameField/>",
        "    <create_parent_folder>Y</create_parent_folder>",
        "    <file>",
        "      <name>%s</name>" % path,
        "      <servlet_output>N</servlet_output>",
        "      <do_not_open_new_file_init>N</do_not_open_new_file_init>",
        "      <extention>csv</extention>",
        "      <append>N</append>",
        "      <split>N</split>",
        "      <haspartno>N</haspartno>",
        "      <add_date>N</add_date>",
        "      <add_time>N</add_time>",
        "      <SpecifyFormat>N</SpecifyFormat>",
        "      <date_time_format/>",
        "      <add_to_result_filenames>Y</add_to_result_filenames>",
        "      <pad>N</pad>",
        "      <fast_dump>N</fast_dump>",
        "      <splitevery/>",
        "    </file>",
        "    <fields>",
    ]
    for f in fields:
        baris += f
    baris += ["    </fields>"]
    baris += tail(x, y)
    return baris


def select_values(nama, fields, x, y, deskripsi=""):
    baris = head(nama, "SelectValues", x, y, deskripsi)
    baris += ["    <fields>"]
    for f in fields:
        baris += f
    baris += [
        "    </fields>",
        "    <select_unspecified>N</select_unspecified>",
    ]
    baris += tail(x, y)
    return baris


def unique_hashset(nama, fields, x, y, deskripsi=""):
    baris = head(nama, "UniqueRowsByHashSet", x, y, deskripsi)
    baris += [
        "    <store_values>Y</store_values>",
        "    <fields>",
    ]
    for f in fields:
        baris += ["      <field>", "        <name>%s</name>" % f, "      </field>"]
    baris += [
        "    </fields>",
        "    <reject_duplicate_row>N</reject_duplicate_row>",
    ]
    baris += tail(x, y)
    return baris


def filter_rows(
    nama, leftvalue, fungsi, text, tipe, true_to, false_to, x, y, deskripsi=""
):
    baris = head(nama, "FilterRows", x, y, deskripsi)
    baris += [
        "    <compare>",
        "      <condition>",
        "        <conditions>",
        "        </conditions>",
        "        <function>%s</function>" % fungsi,
        "        <leftvalue>%s</leftvalue>" % leftvalue,
        "        <negated>N</negated>",
        "        <operator>-</operator>",
        "        <value>",
        "          <isnull>N</isnull>",
        "          <length>-1</length>",
        "          <mask>####0;-####0</mask>",
        "          <name>constant</name>",
        "          <precision>0</precision>",
        "          <text>%s</text>" % text,
        "          <type>%s</type>" % tipe,
        "        </value>",
        "      </condition>",
        "    </compare>",
        "    <send_false_to>%s</send_false_to>" % false_to,
        "    <send_true_to>%s</send_true_to>" % true_to,
    ]
    baris += tail(x, y)
    return baris


def dummy(nama, x, y, deskripsi=""):
    baris = head(nama, "Dummy", x, y, deskripsi)
    baris += tail(x, y)
    return baris


def database_lookup(nama, connection, table, keys, values, x, y, deskripsi=""):
    baris = head(nama, "DBLookup", x, y, deskripsi)
    baris += [
        "    <connection>%s</connection>" % connection,
        "    <cache>N</cache>",
        "    <cache_size>0</cache_size>",
        "    <cache_load_all>N</cache_load_all>",
        "    <lookup>",
        "      <schema>public</schema>",
        "      <table>%s</table>" % table,
    ]
    for stream_field, table_field in keys:
        baris += [
            "      <key>",
            "        <name>%s</name>" % stream_field,
            "        <condition>=</condition>",
            "        <field>%s</field>" % table_field,
            "      </key>",
        ]
    for table_field, new_name, default_value, tipe in values:
        baris += [
            "      <value>",
            "        <name>%s</name>" % table_field,
            "        <rename>%s</rename>" % new_name,
            "        <default>%s</default>" % default_value,
            "        <type>%s</type>" % tipe,
            "      </value>",
        ]
    baris += [
        "      <fail_on_multiple>Y</fail_on_multiple>",
        "      <eat_row_on_failure>N</eat_row_on_failure>",
        "    </lookup>",
    ]
    baris += tail(x, y)
    return baris
