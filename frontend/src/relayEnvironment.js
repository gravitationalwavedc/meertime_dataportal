import {
    Environment,
    RecordSource,
    Store,
} from 'relay-runtime';
import {
    RelayNetworkLayer,
    authMiddleware,
    cacheMiddleware,
    progressMiddleware,
    retryMiddleware,
    uploadMiddleware,
    urlMiddleware,
} from 'react-relay-network-modern';


const network = new RelayNetworkLayer(
    [
        cacheMiddleware({
            size: 100, // max 100 requests
            ttl: 900000, // 15 minutes
        }),
        urlMiddleware({
            url: () => Promise.resolve(process.env.REACT_APP_GRAPHQL_URL),
        }),
        retryMiddleware({
            fetchTimeout: 15000,
            retryDelays: (attempt) => Math.pow(2, attempt + 4) * 100, 
            beforeRetry: ({ forceRetry, abort, attempt }) => {
                if (attempt > 10) abort();
                window.forceRelayRetry = forceRetry;
            },
            statusCodes: [500, 503, 504],
        }),
        authMiddleware({
            token: () => localStorage.jwt,
            prefix: 'JWT '
        }),
        uploadMiddleware(),
    ],
);

const environment = new Environment({
    network,
    store: new Store(new RecordSource()),
});

export default environment;
