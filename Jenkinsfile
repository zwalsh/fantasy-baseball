pipeline {
    agent { docker { image 'python:3.8.1' } }
    stages {
        stage('build') {
            steps {
                sh 'python --version'
            }
        }
    }
}