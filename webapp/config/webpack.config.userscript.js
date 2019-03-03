'use strict';

const paths = require('./paths');
const getClientEnvironment = require('./env');
const publicPath = paths.servedPath;
const shouldUseSourceMap = process.env.GENERATE_SOURCEMAP !== 'false';
const publicUrl = publicPath.slice(0, -1);
const env = getClientEnvironment(publicUrl);
if (env.stringified['process.env'].NODE_ENV !== '"production"') {
    throw new Error('Production builds must have NODE_ENV=production.');
}

// This is the production configuration.
// It compiles slowly and is focused on producing a fast and minimal bundle.
// The development configuration is different and lives in a separate file.
module.exports = {
    mode: 'production',
    bail: true,
    devtool: shouldUseSourceMap ? 'source-map' : false,
    entry: [paths.userScriptIndexJs],
    output: {
        path: paths.appBuild,
        filename: 'index.user.js',
        publicPath: publicPath,
    },
    module: {
        strictExportPresence: true,
        rules: [
            {
                test: /\.(ts|tsx)$/,
                include: paths.appSrc,
                use: [
                    {
                        loader: require.resolve('ts-loader'),
                        options: {
                            // disable type checker - we will use it in fork plugin
                            transpileOnly: true,
                        },
                    },
                ],
            }
        ],
    },
    optimization: {
        minimize: false
    },
};
