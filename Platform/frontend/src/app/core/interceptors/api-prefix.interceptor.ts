import { HttpInterceptorFn } from '@angular/common/http';

import { environment } from '../../../environments/environment';

export const apiPrefixInterceptor: HttpInterceptorFn = (request, next) => {
  let nextRequest = request;
  const token = localStorage.getItem('english_platform_token');

  if (token) {
    nextRequest = nextRequest.clone({
      setHeaders: {
        Authorization: `Token ${token}`,
      },
    });
  }

  if (/^https?:\/\//.test(nextRequest.url)) {
    return next(nextRequest);
  }

  return next(nextRequest.clone({
    url: `${environment.apiUrl}${nextRequest.url.startsWith('/') ? '' : '/'}${nextRequest.url}`,
  }));
};
