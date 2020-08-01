pipeline {
    agent any
    stages {
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
            setBuildStatus('Success', 'SUCCESS')
        }
        unstable {
            echo 'I am unstable :/'
            setBuildStatus('Unstable', 'UNSTABLE')
        }
        failure {
            echo 'I failed :('
            setBuildStatus('Build failure', 'FAILURE')
        }
    }
}

// taken from the Github pipeline example
void setBuildStatus(String message, String state) {
  step([
      $class: "GitHubCommitStatusSetter",
      reposSource: [$class: "ManuallyEnteredRepositorySource", url: "https://github.com/zwalsh/fantasy-baseball"],
      contextSource: [$class: "ManuallyEnteredCommitContextSource", context: "ci/jenkins/build-status"],
      errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
      statusResultSource: [ $class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]] ]
  ]);
}
