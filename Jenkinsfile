pipeline {
    agent any
    environment {
        GITHUB_TOKEN = credentials('github-personal-access-token')
    }
    stages {
        stage('start') {
            steps {
                setBuildStatus('pending')
            }
        }
        stage('test') {
            steps {
                sh 'python3.8 -m unittest'
            }
        }
        stage('lint') {
            steps {
                sh 'find . -type f -name "*.py" | xargs pylint'
            }
        }
    }
    post {
        success {
            echo 'Success!'
            setBuildStatus('SUCCESS')
        }
        unstable {
            echo 'I am unstable :/'
            setBuildStatus('UNSTABLE')
        }
        failure {
            echo 'I failed :('
            setBuildStatus('FAILURE')
        }
    }
}

void setBuildStatus(state) {
    sh """
        curl "https://api.GitHub.com/repos/zwalsh/fantasy-baseball/statuses/$GIT_COMMIT?access_token=$GITHUB_TOKEN" \
                -H "Content-Type: application/json" \
                -X POST \
                -d "{\"state\": \"$state\",\"context\": \"continuous-integration/jenkins\", \"description\": \"Jenkins\", \"target_url\": \"https://jenkins.zachwal.sh/job/fantasy-baseball/$BUILD_NUMBER/console\"}"
    """
}
