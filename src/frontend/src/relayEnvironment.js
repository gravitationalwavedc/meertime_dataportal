import {
  Environment,
  RecordSource,
  Store,
} from 'relay-runtime';
import {
  RelayNetworkLayer,
  urlMiddleware,
  // batchMiddleware,
  // loggerMiddleware,
  // errorMiddleware,
  // perfMiddleware,
  retryMiddleware,
  authMiddleware,
  cacheMiddleware,
  progressMiddleware,
  uploadMiddleware,
} from 'react-relay-network-modern';

const network = new RelayNetworkLayer(
  [
    cacheMiddleware({
      size: 100, // max 100 requests
      ttl: 900000, // 15 minutes
    }),
    urlMiddleware({
      url: () => Promise.resolve('http://localhost:8000/graphql/'),
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
      token: () => sessionStorage.jwt,
      prefix: "JWT "
    }),
    progressMiddleware({
      onProgress: (current, total) => {
        console.log('Downloaded: ' + current + ' B, total: ' + total + ' B');
      },
    }),
    uploadMiddleware(),
  ],
);

const environment = new Environment({
  network,
  store: new Store(new RecordSource()),
});

export default environment;
