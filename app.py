from flask import Flask, render_template, request, redirect
import requests
from bs4 import BeautifulSoup

app = Flask("JobScraper")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# 사이트별 스크래핑

def get_wwr(term):
    # WeWorkRemotely
    url = f"https://weworkremotely.com/remote-jobs/search?utf8=%E2%9C%93&term={term}"
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = []
        # 'section.jobs' 안에 있는 리스트(li) 찾기
        posts = soup.find_all("li", class_="feature")
        for post in posts:
            anchors = post.find_all("a")
            if len(anchors) > 1:
                link = f"https://weworkremotely.com{anchors[1]['href']}"
                title = post.find("span", class_="title").text.strip()
                company = post.find("span", class_="company").text.strip()
                jobs.append({"site": "WWR", "title": title, "company": company, "link": link})
        return jobs
    except:
        return []


def get_web3(term):
    # Web3.career
    url = f"https://web3.career/{term}-jobs"
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = []
        # 테이블의 행(tr) 찾기
        rows = soup.find_all("tr", class_="table_row")
        for row in rows:
            title_tag = row.find("h2")
            if title_tag:
                title = title_tag.text.strip()
                company = row.find("h3").text.strip()
                link = f"https://web3.career{row.find('a')['href']}"
                jobs.append({"site": "Web3", "title": title, "company": company, "link": link})
        return jobs
    except:
        return []


def get_berlin(term):
    # BerlinStartupJobs
    url = f"https://berlinstartupjobs.com/skill-areas/{term}/"
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = []
        ul = soup.find("ul", class_="jobs-list-items")
        if ul:
            posts = ul.find_all("li")
            for post in posts:
                h4 = post.find("h4")
                link = h4.find("a")['href']
                title = h4.text.strip()
                company = post.find("a", class_="bjs-jlid__b").text.strip()
                jobs.append({"site": "Berlin", "title": title, "company": company, "link": link})
        return jobs
    except:
        return []


# 웹사이트 주소 연결

@app.route("/")
def home():
    # 첫 화면
    return render_template("home.html")


@app.route("/search")
def search():
    # 검색 버튼 - 실행
    term = request.args.get("term")
    if not term:
        return redirect("/")

    term = term.lower()  # 소문자로 변환

    # 데이터 수집
    all_jobs = []
    all_jobs.extend(get_wwr(term))
    all_jobs.extend(get_web3(term))
    all_jobs.extend(get_berlin(term))

    # 결과 화면으로 데이터 보내기
    return render_template("results.html", term=term, jobs=all_jobs, count=len(all_jobs))


# 서버 실행
if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
