import fetch from "node-fetch";
import semver from "semver";
import {promises} from "fs";
import yargs from "yargs";


// Types

type GithubResponse<T> = (T & { message: undefined }) | {
    message: string,
    documentation_url: string,
};

interface Milestone {
    title: string,
    id: number
}

interface PullRequest {
    html_url: string,
    number: number
    state: number,
    title: string,
    body: string
    user: {
        login: string,
        avatar_url: string;
        html_url: string;
    },
    merged_at: string,
    milestone: {
        id: number,
    }
    labels: {
        name: string,
        color: string,
    }[],
}

interface Release {
    tag_name: string,
    published_at: string
    body: string
}

// Utils

const githubFetch = async <T>(url: string): Promise<T> => {
    const response = await fetch(url, {headers: {Authorization: "Basic a3l1cmlkZW5hbWlkYTpCYW5uYmFzMTI="}})
        .then(response => response.json() as unknown as GithubResponse<T>) ;
    if (response.message !== undefined) {
        throw Error(`${response.message} ${response.documentation_url}`);
    }
    return response;
}

const fixWrongVersion = (version: string) => {
    if (version === "1.1.7.1") {
        // This is invalid semantic version, but mistakenly released, so handle it specially.
        return "1.1.71";
    }
    return version;
}

const compareVersions = (v1: string, v2: string) => {
    return semver.compare(fixWrongVersion(v1), fixWrongVersion(v2));
}

const isValidVersion = (version: string) => {
    if (version === "1.1.7.1") {
        // This is invalid semantic version, but mistakenly released, so handle it specially.
        return true;
    }
    return semver.valid(version);
}

const fetchMilestonesInNewerOrderUpTo = async (latestVersion: string) => {
    // Explicitly fetch open and closed milestones separately because if we specify "?state=open,closed" together,
    // sometimes a new mile stone is missing.
    const allMilestones = 
          [
              ...(await githubFetch<Milestone[]>("https://api.github.com/repos/kyuridenamida/atcoder-tools/milestones?state=open")),
              ...(await githubFetch<Milestone[]>("https://api.github.com/repos/kyuridenamida/atcoder-tools/milestones?state=closed"))
          ];

    return allMilestones
        // 1.1.8 exists in the milestones now, but will be ignored because it is pending for a special reason.
        .filter(milestone => milestone.title !== "1.1.8")
        .filter(milestone => {
            if (!isValidVersion(milestone.title)) {
                throw Error(`Non-semantic-versioned milestone title: ${milestone.title} has been detected.`);
            }
            return compareVersions(milestone.title, latestVersion) <= 0;
        }).sort((v1, v2) => compareVersions(v1.title, v2.title)).reverse();

}

const fetchPRsByMilestoneId = async () => {
    const pullRequests: PullRequest[] = [];
    for (let page = 1; ; page++) {
        if (page > 50) {
            throw Error("Unexpectedly too many iterations for page: " + page);
        }
        const pullRequestsPartial = await githubFetch<PullRequest[]>(`https://api.github.com/repos/kyuridenamida/atcoder-tools/pulls?state=open,closed&per_page=100&page=${page}`);
        if (pullRequestsPartial.length === 0) {
            break;
        }
        pullRequests.push(...pullRequestsPartial);
    }
    const pullRequestsByTag: { [milestoneId: number]: PullRequest[] } = {};
    pullRequests
        .filter(pr => pr.milestone)
        .forEach(pr => {
            pullRequestsByTag[pr.milestone.id] = pullRequestsByTag[pr.milestone.id] || [];
            pullRequestsByTag[pr.milestone.id].push(pr);
        });
    return pullRequestsByTag;
}

const fetchReleaseByTag = async () => {
    const allReleases = await githubFetch<Release[]>("https://api.github.com/repos/kyuridenamida/atcoder-tools/releases");
    const releaseByTag: { [tagName: string]: Release } = {};
    allReleases.forEach(release => releaseByTag[release.tag_name] = release);
    return releaseByTag;
}

// Main logic

const createChangelog = async (latestVersion: string, changelogMdPath: string) => {
    if (!isValidVersion(latestVersion)) {
        throw Error(`Given version is not valid semantic-versioned: ${latestVersion}`);
    }

    const milestones = await fetchMilestonesInNewerOrderUpTo(latestVersion);
    const releaseByTag = await fetchReleaseByTag();
    const pullRequestsByMilestoneId = await fetchPRsByMilestoneId();
    if (!releaseByTag[latestVersion]) {
        throw Error(`No latest version released: ${latestVersion}`);
    }

    const changeLogMarkdownLines: string[] = [];
    changeLogMarkdownLines.push("# Change Log");
    milestones.forEach(milestone => {
            const release = releaseByTag[milestone.title];
            if (release === undefined) {
                throw Error(`Corresponding release doesn't exist: ${milestone.title}`);
            }
            const pullRequests = pullRequestsByMilestoneId[milestone.id] || [];
            const releaseDate = new Date(release.published_at).toLocaleDateString("ja-JP").replace(/\//g, "-");

            changeLogMarkdownLines.push(`## ${milestone.title} / ${releaseDate}`);
            if (release.body.trim()) {
                changeLogMarkdownLines.push(release.body.trim());
            }
            changeLogMarkdownLines.push("|PR|Change Summary|Label|Author|");
            changeLogMarkdownLines.push("|:---|:---|:---|:---:|");


            pullRequests.forEach(pr => {
                if (pr.labels.find((label) => label.name === "release") !== undefined) {
                    // Exclude Release PRs because they are useless to show
                    return;
                }

                const labels = pr.labels.map(label => `![#${label.color}](https://via.placeholder.com/15/${label.color}/000000?text=+) **${label.name}**`);
                const columns = [
                    `[#${pr.number}](${pr.html_url})`,
                    `${pr.title}`.replace(/\|/g, " "),
                    labels.join("<br/>") || " ",
                    `[${pr.user.login}](${pr.user.html_url})`
                ];
                changeLogMarkdownLines.push(`|${columns.join("|")}|`);
            });
        }
    );
    await promises.writeFile(changelogMdPath, changeLogMarkdownLines.join("\n"));

};

const argv = yargs
    .option('releaseVersion', {
        description: 'Release version to create the change log file with',
        type: 'string',
        demandOption: true,
    })
    .option('changeLogOutputFile', {
        description: 'Generated change log path',
        type: 'string',
        default: "./CHANGELOG.md"
    })
    .help()
    .alias('help', 'h')
    .argv;

console.log(argv);
createChangelog(argv.releaseVersion, argv.changeLogOutputFile);
