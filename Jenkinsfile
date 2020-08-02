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
                sh 'python3.8 -m xmlrunner -o test-reports'
            }
        }
        stage('lint') {
            steps {
                sh 'find . -type f -name "*.py" | xargs pylint --rcfile=pylintrc'
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
