import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPE_DIR = os.path.join(ROOT, "pipelines")
WF_DIR = os.path.join(ROOT, "workflows")

NAMA_BULAN = [
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
]
NAMA_HARI = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]


def head(nama, ttype, x, y, deskripsi=""):
    return [
        "  <transform>",
        "    <name>%s</name>" % nama,
        "    <type>%s</type>" % ttype,
        "    <description>%s</description>" % deskripsi,
        "    <distribute>Y</distribute>",
        "    <custom_distribution/>",
        "    <copies>1</copies>",
        "    <partitioning>",
        "      <method>none</method>",
        "      <schema_name/>",
        "    </partitioning>",
    ]


def tail(x, y):
    return [
        "    <attributes/>",
        "    <GUI>",
        "      <xloc>%d</xloc>" % x,
        "      <yloc>%d</yloc>" % y,
        "    </GUI>",
        "  </transform>",
    ]


def csv_field(nama, ftype="String", fmt="", length=-1, precision=-1):
    return [
        "      <field>",
        "        <name>%s</name>" % nama,
        "        <type>%s</type>" % ftype,
        "        <format>%s</format>" % fmt,
        "        <currency/>",
        "        <decimal>.</decimal>",
        "        <group/>",
        "        <length>%d</length>" % length,
        "        <precision>%d</precision>" % precision,
        "        <trim_type>both</trim_type>",
        "      </field>",
    ]


def out_field(nama, ftype="String"):
    return [
        "      <field>",
        "        <name>%s</name>" % nama,
        "        <rename>%s</rename>" % nama,
        "        <type>%s</type>" % ftype,
        "        <length>-1</length>",
        "        <precision>-1</precision>",
        "        <replace>N</replace>",
        "        <scriptResult>N</scriptResult>",
        "      </field>",
    ]


def sel_field(nama, rename):
    return [
        "      <field>",
        "        <name>%s</name>" % nama,
        "        <rename>%s</rename>" % rename,
        "        <length>-2</length>",
        "        <precision>-2</precision>",
        "      </field>",
    ]


def text_field(nama, fmt=""):
    return [
        "      <field>",
        "        <name>%s</name>" % nama,
        "        <type>String</type>",
        "        <format>%s</format>" % fmt,
        "        <currency/>",
        "        <decimal/>",
        "        <group/>",
        "        <nullif/>",
        "        <trim_type>both</trim_type>",
        "        <length>-1</length>",
        "        <precision>-1</precision>",
        "      </field>",
    ]


def date_field(nama, fmt="yyyy-MM-dd"):
    return [
        "      <field>",
        "        <name>%s</name>" % nama,
        "        <type>Date</type>",
        "        <format>%s</format>" % fmt,
        "        <currency/>",
        "        <decimal/>",
        "        <group/>",
        "        <nullif/>",
        "        <trim_type>none</trim_type>",
        "        <length>-1</length>",
        "        <precision>-1</precision>",
        "      </field>",
    ]


def pipeline(nama, deskripsi, hops, transforms):
    baris = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<pipeline>",
        "  <info>",
        "    <name>%s</name>" % nama,
        "    <name_sync_with_filename>Y</name_sync_with_filename>",
        "    <description>%s</description>" % deskripsi,
        "    <extended_description/>",
        "    <pipeline_version/>",
        "    <pipeline_type>Normal</pipeline_type>",
        "    <parameters>",
        "    </parameters>",
        "    <capture_transform_performance>N</capture_transform_performance>",
        "    <transform_performance_capturing_delay>1000</transform_performance_capturing_delay>",
        "    <transform_performance_capturing_size_limit>100</transform_performance_capturing_size_limit>",
        "    <created_user>-</created_user>",
        "    <created_date>2026/10/21 09:00:00.000</created_date>",
        "    <modified_user>-</modified_user>",
        "    <modified_date>2026/10/21 09:00:00.000</modified_date>",
        "  </info>",
        "  <notepads>",
        "  </notepads>",
        "  <order>",
    ]
    for a, b in hops:
        baris += [
            "    <hop>",
            "      <from>%s</from>" % a,
            "      <to>%s</to>" % b,
            "      <enabled>Y</enabled>",
            "    </hop>",
        ]
    baris += ["  </order>"]
    for t in transforms:
        baris += t
    baris += [
        "  <attributes>",
        "  </attributes>",
        "  <GUI>",
        "    <xloc>50</xloc>",
        "    <yloc>50</yloc>",
        "  </GUI>",
        "</pipeline>",
        "",
    ]
    return "\n".join(baris)


def tulis(nama_berkas, isi):
    with io.open(
        os.path.join(PIPE_DIR, nama_berkas), "w", encoding="utf-8", newline="\n"
    ) as f:
        f.write(isi)
    print("WROTE " + nama_berkas)


def xml_escape(teks):
    return (
        teks.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def script_transform(nama, bahasa, badan, fields, x, y, deskripsi=""):
    baris = head(nama, "SuperScript", x, y, deskripsi)
    baris += [
        "    <scriptLanguage>%s</scriptLanguage>" % bahasa,
        "    <scripts>",
        "      <script>",
        "        <scriptType>0</scriptType>",
        "        <scriptName>Transform</scriptName>",
        "        <scriptBody>%s</scriptBody>" % xml_escape(badan),
        "      </script>",
        "    </scripts>",
        "    <fields>",
    ]
    for f in fields:
        baris += f
    baris += ["    </fields>"]
    baris += tail(x, y)
    return baris
