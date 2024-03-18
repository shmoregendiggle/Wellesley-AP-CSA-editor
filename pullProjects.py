#!/usr/bin/python3
import collections.abc
#hyper needs the four following aliases to be done manually.
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping
#Now import hyper
import requests
import canvasapi
from canvasapi import Canvas
from requests import get
import os
import secrets
from bs4 import BeautifulSoup
import re
import gdown
import shutil
import zipfile
from datetime import datetime
import gdown
import docx
import shutil

BASEURL = "https://wellesley.instructure.com/"
def getTerm(day, month):
    terms = [(-1, 10), (1, 22), (4, 2), (6, 30)]
    if month > 7:
        month -= 12
    term = 1
    for i in range(len(terms)):
        if month > terms[i][0] or month == terms[i][0] and day > terms[i][1]:
            term = i + 2
    return term

def download_google_doc_as_docx(doc_url, output_path):
    file_id = doc_url.split('/')[-2]
    docx_url = f'https://drive.google.com/uc?id={file_id}&export=download'
    gdown.download(docx_url, output_path, quiet=True)

def extract_text_from_docx(docx_path):
    text = ""
    doc = docx.Document(docx_path)
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def submitAssignment(filepath, assignment):
    assignment.submit({"submission_type":"online_upload"}, file=filepath)

def pullAssignments(token, labsFolder):
    today = datetime.today()
    term = getTerm(today.day, today.month)
    pathsAssignments = {}
    api = canvasapi.Canvas(BASEURL, token)
    course = api.get_course(38471)
    user = api.get_user('self')
    assignments = course.get_assignments()
    try:
        os.mkdir(labsFolder)
    except:
        pass
    for assignment in assignments:
        print(dir(assignment))
        sLabPage = BeautifulSoup(str(assignment.to_json), "html.parser")
        pageAs = sLabPage.find_all("a", class_="inline_disabled")
        date = assignment.updated_at_date
        assignmentTerm = getTerm(date.day, date.month)
        if assignment.get_submission(user).submitted_at is not None or assignmentTerm != term:
            if os.path.exists(os.path.join(labsFolder, assignment.name)):
                shutil.rmtree(os.path.join(labsFolder, assignment.name))
                print(assignment.name + " is deleted")
            print(assignment.name + " is continued")
            continue
        pageLinks = []
        for a in pageAs:
            pageLinks.append(a.get("href"))
        drivePattern = re.compile(r'https://drive\.google\.com/file/d/[^,\s]*')
        driveLinks = [element for element in pageLinks if drivePattern.search(element)]
        docPattern = re.compile(r'https://docs\.google\.com/document/d/[^,\s]*')
        docLinks = [element for element in pageLinks if docPattern.search(element)]
        labFolder = ""
        if docLinks or driveLinks:
            labFolder = os.path.join(labsFolder, assignment.name)
            
            try:
                print(assignment.name + " folder is created")
                os.mkdir(os.path.join(labsFolder, assignment.name))
            except:
                print(assignment.name + " already exists")
                continue
        else:
            print(assignment.name + " folder is not created")
            print(pageLinks)
        if docLinks:
            docLink = docLinks[0]
            docX = os.path.join(labFolder, "output.docx")
            download_google_doc_as_docx(docLink, docX)
            textContent = extract_text_from_docx(docX)
            with open(os.path.join(labFolder, "instructions.txt"), 'w', encoding='utf-8') as file:
                file.write(textContent)
            os.remove(docX)
        if driveLinks:
            driveLink = driveLinks[0]
            file_id = driveLink.split('/')[-2]
            downloadedFile = gdown.download(id=file_id, quiet=True, use_cookies=False)
            if downloadedFile.endswith(".zip"):
                zipfile.ZipFile(downloadedFile, "r").extractall(labFolder)
                os.remove(downloadedFile)
            else:
                shutil.move("./" + downloadedFile, os.path.join(labFolder, downloadedFile))
            if os.path.join(labFolder, downloadedFile).endswith(".pdf"):
                os.remove(os.path.join(labFolder, downloadedFile))
                try:
                    os.rmdir(labFolder)
                except:
                    pass
            else:
                pathsAssignments[labFolder] = assignment
        else:
            if docLinks:
                pathsAssignments[labFolder] = assignment
                open(os.path.join(labFolder, "main.java"), 'w')

    return pathsAssignments
