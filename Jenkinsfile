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
        stage('pip') {
            steps {
                sh 'python3.8 -m pip install -r requirements.txt'
                sh 'python3.8 -m pip install -r requirements-test.txt'
            }
        }
        stage('test') {
            steps {
                sh 'python3.8 -m xmlrunner -o test-reports'
            }
        }
        stage('lint-warnings-errors') {
            steps {
                sh 'find . -type f -name "*.py" | xargs -P 4 python3.8 -m pylint --rcfile=pylintrc --disable=R,C --output-format=junit | tee pylint-we.out'
                sh 'exit ${PIPESTATUS[0]}'
            }
        }
        stage('lint-conventions-refactors') {
            steps {
                sh 'find . -type f -name "*.py" | xargs -P 4 python3.8 -m pylint --rcfile=pylintrc --fail-under=9'
            }
        }
    }
    post {
        success {
            echo 'Success!'
            setBuildStatus('success')
        }
        unstable {
            echo 'I am unstable :/'
            setBuildStatus('failure')
        }
        failure {
            echo 'I failed :('
            setBuildStatus('failure')
        }
        always {
            junit 'test-reports/*.xml'
            junit 'pylint-we.out'
        }
    }
}

void setBuildStatus(state) {
    sh """
        curl "https://api.GitHub.com/repos/zwalsh/fantasy-baseball/statuses/$GIT_COMMIT?access_token=$GITHUB_TOKEN" \
                -H "Content-Type: application/json" \
                -X POST \
                -d '{\"state\": \"$state\",\"context\": \"continuous-integration/jenkins\", \"description\": \"Jenkins\", \"target_url\": \"https://jenkins.zachwal.sh/job/fantasy-baseball/$BUILD_NUMBER/console\"}'
    """
}
